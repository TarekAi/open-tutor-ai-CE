"""
Database module for OpenTutorAI

This module defines the database tables specific to OpenTutorAI while using
the same database connection as OpenWebUI to maintain compatibility.
"""

from datetime import datetime
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Float,
    Integer,
    Numeric,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship, sessionmaker
from open_webui.internal.db import Base, engine, get_db, JSONField

PREFIX = "opentutorai_"


class Support(Base):
    """
    Table for storing student support requests.
    Each support request is linked to a chat in the Open WebUI chat table.
    """

    __tablename__ = f"{PREFIX}support"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    custom_subject = Column(String, nullable=True)
    course_id = Column(String, nullable=True)
    learning_objective = Column(Text, nullable=True)
    learning_type = Column(String, nullable=True)
    level = Column(String, nullable=False)
    content_language = Column(String, nullable=True, default="English")
    estimated_duration = Column(String, nullable=True)
    access_type = Column(String, nullable=True, default="Private")
    keywords = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    avatar_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="open")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    meta_data = Column(JSONField, nullable=True)

    chat_id = Column(
        String, ForeignKey("chat.id", ondelete="CASCADE"), index=True, nullable=True
    )

    def __repr__(self):
        return f"<Support(id={self.id}, user_id={self.user_id}, title={self.title})>"


class SupportFile(Base):
    """
    Table for storing files attached to support requests.
    """

    __tablename__ = f"{PREFIX}support_file"

    id = Column(String, primary_key=True, index=True)
    support_id = Column(
        String, ForeignKey(f"{PREFIX}support.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    support = relationship("Support", backref="files")

    def __repr__(self):
        return f"<SupportFile(id={self.id}, support_id={self.support_id}, filename={self.filename})>"


#################################################
############## La partie Teacher ################
#################################################


# Classes, Assignments, Enrollments, Student Activities, Course Content, Course Files
class Classe(Base):
    """Table for storing class information"""

    __tablename__ = f"{PREFIX}classe"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course = Column(String, nullable=True)
    user_id = Column(String, index=True, nullable=False)
    student_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    assignments = relationship(
        "Assignment", back_populates="classe", cascade="all, delete-orphan"
    )
    enrollments = relationship(
        "Enrollment", back_populates="classe", cascade="all, delete-orphan"
    )
    courses = relationship(
        "CourseContent", back_populates="classe", cascade="all, delete-orphan"
    )


class Assignment(Base):
    """Table for storing assignment information"""

    __tablename__ = f"{PREFIX}assignment"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    classe_id = Column(
        String, ForeignKey(f"{PREFIX}classe.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(String, index=True, nullable=False)
    deadline = Column(DateTime, nullable=True)
    points = Column(Integer, default=100)
    status = Column(String, default="Active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    max_submissions = Column(Integer, default=0)
    current_submissions = Column(Integer, default=0)

    classe = relationship("Classe", back_populates="assignments")


class Enrollment(Base):
    """Table for storing student enrollments in classes"""

    __tablename__ = f"{PREFIX}enrollment"

    id = Column(String, primary_key=True, index=True)
    classe_id = Column(
        String, ForeignKey(f"{PREFIX}classe.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    points = Column(Integer, default=0)
    grade = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    joined_at = Column(BigInteger)

    # Relationships
    classe = relationship("Classe", back_populates="enrollments")
    user = relationship("User", foreign_keys=[user_id])


class StudentActivity(Base):
    """Table for tracking student activities and points"""

    __tablename__ = f"{PREFIX}student_activities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    classe_id = Column(
        String, ForeignKey(f"{PREFIX}classe.id", ondelete="CASCADE"), nullable=True
    )
    action_type = Column(String)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class CourseContent(Base):
    """Table for storing course content information"""

    __tablename__ = f"{PREFIX}course_content"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)  # course / td / tp
    classe_id = Column(
        String, ForeignKey(f"{PREFIX}classe.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    classe = relationship("Classe", back_populates="courses")
    files = relationship(
        "CourseFile", back_populates="course", cascade="all, delete-orphan"
    )


class CourseFile(Base):
    """Table for storing files associated with course content"""

    __tablename__ = f"{PREFIX}course_files"

    id = Column(String, primary_key=True, index=True)
    course_id = Column(
        String,
        ForeignKey(f"{PREFIX}course_content.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())

    # Relationship
    course = relationship("CourseContent", back_populates="files")


######################################################################


def init_database():
    """
    Initialize the database tables for OpenTutorAI.
    Call this function when your app starts to ensure all tables exist.

    This is safe to call even if tables already exist, as SQLAlchemy's
    create_all() only creates tables that don't exist yet.
    """
    from open_webui.internal.db import engine

    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("OpenTutorAI database tables initialized successfully")

    return engine
