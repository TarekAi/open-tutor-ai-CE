from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from pydantic import BaseModel
import logging
import uuid
import shutil
import os
from datetime import datetime

from open_webui.utils.auth import get_current_user
from open_webui.internal.db import engine
from open_tutorai.models.database import CourseFile, Classe, CourseContent
from sqlalchemy.orm import sessionmaker

log = logging.getLogger(__name__)
log.setLevel("INFO")

router = APIRouter()

BASE_UPLOAD_DIR = "data/uploads/classes"

ALLOWED_FILES = ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "zip"]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# -------- Response Model --------


class CourseFileResponse(BaseModel):
    id: str
    course_id: str
    filename: str
    file_path: str
    file_type: str | None
    file_size: int | None

    class Config:
        from_attributes = True


# -------- Database Session --------


def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


# -------- Create Class Folder Structure --------


def create_class_folders(class_id: str):

    class_folder = os.path.join(BASE_UPLOAD_DIR, class_id)

    folders = ["courses", "td", "tp", "exams"]

    for folder in folders:
        path = os.path.join(class_folder, folder)
        os.makedirs(path, exist_ok=True)

    return class_folder


# -------- Upload File --------
@router.post("/upload/{course_id}/{section}", response_model=CourseFileResponse)
async def upload_file(
    course_id: str,
    section: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):

    session = get_db_session()
    try:

        # validate section
        if section not in ["courses", "td", "tp", "exams"]:
            raise HTTPException(status_code=400, detail="Invalid section")

        # validate extension
        ext = file.filename.split(".")[-1].lower()

        if ext not in ALLOWED_FILES:
            raise HTTPException(status_code=400, detail="File type not allowed")

        # read file
        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        await file.seek(0)

        # get course
        course = (
            session.query(CourseContent)
            .filter(CourseContent.id == course_id, CourseContent.user_id == user.id)
            .first()
        )

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # class id
        class_id = course.classe_id

        # create folders
        create_class_folders(class_id)

        # generate id
        file_id = str(uuid.uuid4())

        safe_filename = file.filename.replace(" ", "_")

        # path on disk
        upload_path = os.path.join(
            BASE_UPLOAD_DIR, class_id, section, f"{file_id}_{safe_filename}"
        )

        # save file
        with open(upload_path, "wb") as buffer:
            buffer.write(contents)

        # file path stored in DB
        db_path = f"/uploads/classes/{class_id}/{section}/{file_id}_{safe_filename}"

        # create DB record
        new_file = CourseFile(
            id=file_id,
            course_id=course_id,
            filename=safe_filename,
            file_path=db_path,
            file_type=ext,
            file_size=len(contents),
            uploaded_at=datetime.now(),
        )

        session.add(new_file)
        session.commit()
        session.refresh(new_file)

        return new_file

    finally:
        session.close()


# -------- Get Files --------
@router.get("/course/{course_id}", response_model=List[CourseFileResponse])
async def get_course_files(course_id: str, user=Depends(get_current_user)):

    session = get_db_session()

    try:

        course = (
            session.query(CourseContent)
            .filter(CourseContent.id == course_id, CourseContent.user_id == user.id)
            .first()
        )

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        files = (
            session.query(CourseFile)
            .filter(CourseFile.course_id == course_id)
            .order_by(CourseFile.uploaded_at.desc())
            .all()
        )

        return files

    finally:
        session.close()


# -------- Delete File --------
@router.delete("/{file_id}")
async def delete_file(file_id: str, user=Depends(get_current_user)):

    session = get_db_session()

    try:

        file = session.query(CourseFile).filter(CourseFile.id == file_id).first()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        file_path = os.path.join("data", file.file_path.lstrip("/"))

        print("Deleting:", file_path)

        if os.path.exists(file_path):
            os.remove(file_path)

        session.delete(file)
        session.commit()

        return {"status": "success", "message": "File deleted"}

    finally:
        session.close()
