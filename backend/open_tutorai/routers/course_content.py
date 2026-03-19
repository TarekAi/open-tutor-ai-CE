from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
import os
from open_webui.utils.auth import get_current_user
from open_webui.internal.db import engine
from open_tutorai.models.database import CourseContent, Classe
from sqlalchemy.orm import sessionmaker

log = logging.getLogger(__name__)
log.setLevel("INFO")

router = APIRouter()


# -------- Pydantic Models --------
class CourseCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    type: str
    classe_id: str


class CourseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    type: str
    classe_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# -------- Database Session --------
def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


# -------- Create Course --------
@router.post("/create", response_model=CourseResponse)
async def create_course(data: CourseCreateRequest, user=Depends(get_current_user)):
    session = get_db_session()

    try:
        classe = (
            session.query(Classe)
            .filter(Classe.id == data.classe_id, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

        course_id = str(uuid.uuid4())

        new_course = CourseContent(
            id=course_id,
            title=data.title,
            description=data.description,
            type=data.type,
            classe_id=data.classe_id,
            user_id=user.id,
            created_at=datetime.now(),
        )

        session.add(new_course)
        session.commit()
        session.refresh(new_course)

        log.info(f"Course created {course_id}")

        return new_course

    except Exception as e:
        session.rollback()
        log.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()


# -------- Get Courses By Classe --------
@router.get("/classe/{classe_id}", response_model=List[CourseResponse])
async def get_courses_by_class(classe_id: str, user=Depends(get_current_user)):

    session = get_db_session()
    try:
        classe = (
            session.query(Classe)
            .filter(Classe.id == classe_id, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

        courses = (
            session.query(CourseContent)
            .filter(CourseContent.classe_id == classe_id)
            .order_by(CourseContent.created_at.desc())
            .all()
        )

        return courses

    finally:
        session.close()


# -------- Get Single Course --------
@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(course_id: str, user=Depends(get_current_user)):

    session = get_db_session()
    try:
        course = (
            session.query(CourseContent)
            .filter(CourseContent.id == course_id, CourseContent.user_id == user.id)
            .first()
        )

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        return course
    finally:
        session.close()


# -------- Delete Course --------
@router.delete("/{course_id}")
async def delete_course(course_id: str, user=Depends(get_current_user)):

    session = get_db_session()
    try:

        course = (
            session.query(CourseContent)
            .filter(CourseContent.id == course_id, CourseContent.user_id == user.id)
            .first()
        )

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        for f in course.files:

            file_path = os.path.join("data", f.file_path.lstrip("/"))

            if os.path.exists(file_path):
                os.remove(file_path)

            session.delete(f)

        # delete course
        session.delete(course)
        session.commit()

        return {"status": "success", "message": "Course and files deleted"}

    finally:
        session.close()


# -------- Get Class Content --------
@router.get("/classe/{classe_id}/content")
async def get_class_content(classe_id: str, user=Depends(get_current_user)):

    session = get_db_session()

    try:

        classe = (
            session.query(Classe)
            .filter(Classe.id == classe_id, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

        # get all course contents
        contents = (
            session.query(CourseContent)
            .filter(CourseContent.classe_id == classe_id)
            .order_by(CourseContent.created_at.desc())
            .all()
        )

        courses = []
        tds = []
        tps = []
        exams = []

        for c in contents:

            file = c.files[0] if len(c.files) > 0 else None

            item = {
                "id": c.id,
                "title": c.title,
                "type": file.file_type if file else "doc",
                "size": file.file_size if file else None,
                "date": c.created_at,
                "file": {
                    "url": file.file_path if file else None,
                    "name": file.filename if file else None,
                },
            }

            if c.type == "course":
                courses.append(item)

            elif c.type == "td":
                tds.append(item)

            elif c.type == "tp":
                tps.append(item)

            elif c.type == "exam":
                exams.append(item)

        return {"courses": courses, "tds": tds, "tps": tps, "exams": exams}

    finally:
        session.close()
