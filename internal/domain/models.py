"""Доменные модели CheckIn."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: Optional[str] = None
    role_id: str = ""
    group_id: Optional[str] = None
    department_id: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    password_hash: str = ""
    created_at: Optional[datetime] = None

    def to_public_dict(self) -> dict:
        return {"user_id": str(self.user_id) if self.user_id else None,
                "role_id": str(self.role_id) if self.role_id else None,
                "group_id": str(self.group_id) if self.group_id else None,
                "department_id": str(self.department_id) if self.department_id else None,
                "first_name": self.first_name, "last_name": self.last_name,
                "email": self.email, "phone": self.phone,
                "created_at": self.created_at.isoformat() if self.created_at else None}

@dataclass
class Subject:
    subject_id: Optional[str] = None
    name: str = ""

@dataclass
class Attendance:
    attendance_id: Optional[str] = None
    lesson_id: str = ""
    student_id: str = ""
    qr_session_id: Optional[str] = None
    marked_by: Optional[str] = None
    status: str = "absent"
    method: str = "manual"
    marked_at: Optional[datetime] = None

@dataclass
class Lesson:
    lesson_id: Optional[str] = None
    subject_id: str = ""
    group_id: str = ""
    teacher_id: str = ""
    lesson_date: Optional[datetime] = None
    lesson_type: str = "lecture"
    created_at: Optional[datetime] = None

@dataclass
class QRSession:
    qr_session_id: Optional[str] = None
    lesson_id: str = ""
    token: str = ""
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str = "active"
    closed_at: Optional[datetime] = None
