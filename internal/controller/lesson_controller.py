"""HTTP-маршруты занятий: только DTO, вызов сервиса и HTTP-ответ."""
from fastapi import APIRouter, Request, Response
from typing import List
from internal.domain.models import Lesson
from internal.controller.dto import LessonCreateDTO, LessonUpdateDTO, LessonResponseDTO
from internal.controller.error_mapping import to_http_exception

router = APIRouter(prefix="/api/v1/lessons", tags=["Lessons"])

def _dto(item): return LessonResponseDTO(**item.__dict__)

def _service(request): return request.app.state.lesson_service

@router.post("", response_model=LessonResponseDTO, status_code=201)
def create_lesson(payload: LessonCreateDTO, request: Request, response: Response):
    try:
        item = _service(request).create(Lesson(**payload.model_dump()))
        response.headers["Location"] = "/api/v1/lessons/" + str(item.lesson_id)
        return _dto(item)
    except Exception as exc: raise to_http_exception(exc)

@router.get("", response_model=List[LessonResponseDTO])
def list_lessons(request: Request, limit: int = 20, offset: int = 0):
    try: return [_dto(x) for x in _service(request).list(limit, offset)]
    except Exception as exc: raise to_http_exception(exc)

@router.get("/{lesson_id}", response_model=LessonResponseDTO)
def get_lesson(lesson_id: str, request: Request):
    try: return _dto(_service(request).get(lesson_id))
    except Exception as exc: raise to_http_exception(exc)

@router.put("/{lesson_id}", response_model=LessonResponseDTO)
def update_lesson(lesson_id: str, payload: LessonUpdateDTO, request: Request):
    try:
        item = Lesson(lesson_id=lesson_id, **payload.model_dump())
        return _dto(_service(request).update(item))
    except Exception as exc: raise to_http_exception(exc)

@router.delete("/{lesson_id}", status_code=204)
def delete_lesson(lesson_id: str, request: Request):
    try: _service(request).delete(lesson_id); return Response(status_code=204)
    except Exception as exc: raise to_http_exception(exc)
