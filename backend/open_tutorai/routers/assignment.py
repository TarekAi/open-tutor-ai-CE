from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from sqlalchemy import case, desc
from sqlalchemy.orm import sessionmaker
from open_webui.utils.auth import get_current_user
from open_webui.internal.db import engine
from open_tutorai.models.database import Assignment, Classe, Base

log = logging.getLogger(__name__)
log.setLevel("INFO")

router = APIRouter()


# --- Pydantic Models ---
class AssignmentCreateRequest(BaseModel):
    title: str
    description: str
    classe_id: str
    deadline: datetime
    points: int


class AssignmentResponse(BaseModel):
    id: str
    title: str
    description: str
    classe_id: str
    classe_name: str
    user_id: str
    deadline: datetime
    points: int
    status: str
    max_submissions: int
    current_submissions: int

    class Config:
        from_attributes = True


def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


# --- Helper Functions ---
def sync_assignment_status(session, assignment):
    """Sync the status: Pending (Deadline fat) takes priority over Completed."""
    now = datetime.now()
    curr = assignment.current_submissions or 0
    mx = assignment.max_submissions or 0
    new_status = "Active"

    if assignment.deadline and now > assignment.deadline:
        new_status = "Pending"

    elif mx > 0 and curr >= mx:
        new_status = "Completed"

    else:
        new_status = "Active"

    if assignment.status != new_status:
        assignment.status = new_status

    return new_status


# --- Routes ---
# Create, List, Update, Delete Assignments and Get Stats


# create assignment
@router.post("/create", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreateRequest, user=Depends(get_current_user)
):
    """Create a new assignment for a class."""
    session = get_db_session()
    try:
        assignment_id = str(uuid.uuid4())
        classe = (
            session.query(Classe).filter(Classe.id == assignment_data.classe_id).first()
        )
        student_total = classe.student_count if (classe and classe.student_count) else 0

        new_assignment = Assignment(
            id=assignment_id,
            title=assignment_data.title,
            description=assignment_data.description,
            classe_id=assignment_data.classe_id,
            user_id=user.id,
            points=assignment_data.points,
            deadline=assignment_data.deadline,
            created_at=datetime.now(),
            max_submissions=student_total,
            current_submissions=0,
            status="Active",
        )

        session.add(new_assignment)
        session.commit()
        session.refresh(new_assignment)
        response_data = {
            "id": new_assignment.id,
            "title": new_assignment.title,
            "description": new_assignment.description,
            "classe_id": new_assignment.classe_id,
            "classe_name": classe.name if classe else "Unknown",
            "user_id": new_assignment.user_id,
            "deadline": new_assignment.deadline,
            "points": new_assignment.points,
            "status": new_assignment.status,
            "max_submissions": new_assignment.max_submissions,
            "current_submissions": new_assignment.current_submissions,
        }
        return response_data
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# get all assignments
@router.get("/all", response_model=List[AssignmentResponse])
async def list_Assignment(user=Depends(get_current_user)):
    """List all assignments for the current user, sorted by status and creation date."""
    session = get_db_session()
    try:
        status_priority = case(
            {"Active": 1, "Pending": 2, "Completed": 3}, value=Assignment.status
        )
        results = (
            session.query(Assignment, Classe.name.label("classe_name"))
            .join(Classe, Assignment.classe_id == Classe.id)
            .filter(Assignment.user_id == user.id)
            .order_by(status_priority.asc(), Assignment.created_at.desc())
            .all()
        )

        assignments_data = []
        for assign, c_name in results:
            sync_assignment_status(session, assign)
            d = {
                "id": assign.id,
                "title": assign.title,
                "description": assign.description,
                "classe_id": assign.classe_id,
                "classe_name": c_name,
                "user_id": assign.user_id,
                "deadline": assign.deadline,
                "points": assign.points,
                "status": assign.status,
                "max_submissions": assign.max_submissions,
                "current_submissions": assign.current_submissions,
            }
            assignments_data.append(d)
        session.commit()
        return assignments_data
    except Exception as e:
        log.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# get statistiques of assignments
@router.get("/stats")
async def get_assignment_stats(user=Depends(get_current_user)):
    """Get statistics about the user's assignments, including counts by status and submission rates."""
    session = get_db_session()
    try:
        all_assignments = (
            session.query(Assignment).filter(Assignment.user_id == user.id).all()
        )

        for a in all_assignments:
            sync_assignment_status(session, a)
        session.commit()

        total = len(all_assignments)
        active_count = len([a for a in all_assignments if a.status == "Active"])
        pending_count = len([a for a in all_assignments if a.status == "Pending"])
        completed_count = len([a for a in all_assignments if a.status == "Completed"])
        total_subs = sum([a.current_submissions for a in all_assignments])
        total_max = sum([a.max_submissions for a in all_assignments])

        if total_max > 0:
            raw_avg_rate = (total_subs / total_max) * 100
            avg_rate = min(int(raw_avg_rate), 100)
        else:
            avg_rate = 0

        if total > 0:
            raw_completion = (completed_count / total) * 100
            completion_rate = min(int(raw_completion), 100)
        else:
            completion_rate = 0
        # ------------------------------------------------

        last_week = datetime.now() - timedelta(days=7)
        new_this_week = len([a for a in all_assignments if a.created_at >= last_week])

        now = datetime.now()
        overdue_count = len(
            [a for a in all_assignments if a.status == "Pending" and a.deadline < now]
        )
        completion_change = "+2% this week" if completion_rate > 0 else "No change"

        return {
            "total": total,
            "total_change": f"+{new_this_week} this week",
            "avg_rate": f"{avg_rate}%",
            "avg_rate_change": "+2% trend" if avg_rate > 0 else "0%",
            "pending": pending_count,
            "pending_change": (
                f"{overdue_count} overdue" if overdue_count > 0 else "All caught up"
            ),
            "completion": f"{completion_rate}%",
            "completion_change": completion_change,
        }

    except Exception as e:
        log.error(f"Error in stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not calculate stats")
    finally:
        session.close()


# update assignment
@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    assignment_data: AssignmentCreateRequest,
    user=Depends(get_current_user),
):
    """Update an existing assignment."""
    session = get_db_session()
    try:
        assignment = (
            session.query(Assignment)
            .filter(Assignment.id == assignment_id, Assignment.user_id == user.id)
            .first()
        )

        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")

        assignment.title = assignment_data.title
        assignment.description = assignment_data.description
        assignment.deadline = assignment_data.deadline
        assignment.points = assignment_data.points
        assignment.classe_id = assignment_data.classe_id

        session.commit()
        session.refresh(assignment)

        classe = session.query(Classe).filter(Classe.id == assignment.classe_id).first()

        return {
            **assignment.__dict__,
            "classe_name": classe.name if classe else "Unknown Class",
        }
    except Exception as e:
        session.rollback()
        log.error(f"Error updating: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# delete assignment
@router.delete("/{assignment_id}")
async def delete_assignment(assignment_id: str, user=Depends(get_current_user)):
    """Delete an existing assignment."""
    session = get_db_session()
    try:
        assignment = (
            session.query(Assignment)
            .filter(Assignment.id == assignment_id, Assignment.user_id == user.id)
            .first()
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Not found")
        session.delete(assignment)
        session.commit()
        return {"status": "success"}
    finally:
        session.close()
