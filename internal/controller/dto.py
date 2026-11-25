"""DTO запросов и ответов. Секретный QR token не включается в публичный DTO."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class LessonCreateDTO(BaseModel):
    subject_id: str
    group_id: str
    teacher_id: str
    lesson_date: datetime
    lesson_type: str = "lecture"

class LessonUpdateDTO(LessonCreateDTO): pass

class LessonResponseDTO(BaseModel):
    lesson_id: str
    subject_id: str
    group_id: str
    teacher_id: str
    lesson_date: datetime
    lesson_type: str
    created_at: Optional[datetime] = None

class QRSessionCreateDTO(BaseModel):
    ttl_minutes: int = Field(default=5, ge=1, le=15)

class QRSessionResponseDTO(BaseModel):
    qr_session_id: str
    lesson_id: str
    created_at: datetime
    expires_at: datetime
    status: str
    closed_at: Optional[datetime] = None
