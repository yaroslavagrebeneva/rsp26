"""HTTP-маршруты QR-сессий."""
from fastapi import APIRouter, Request, Response
from typing import List
from internal.controller.dto import QRSessionCreateDTO, QRSessionResponseDTO
from internal.controller.error_mapping import to_http_exception

router = APIRouter(tags=["QR Sessions"])
def _dto(item): return QRSessionResponseDTO(qr_session_id=str(item.qr_session_id), lesson_id=str(item.lesson_id),
    created_at=item.created_at, expires_at=item.expires_at, status=item.status, closed_at=item.closed_at)
def _service(request): return request.app.state.qr_session_service

@router.post("/api/v1/lessons/{lesson_id}/qr-sessions", response_model=QRSessionResponseDTO, status_code=201)
def create_qr_session(lesson_id: str, request: Request, response: Response, payload: QRSessionCreateDTO = QRSessionCreateDTO()):
    try:
        item = _service(request).create(lesson_id, payload.ttl_minutes)
        response.headers["Location"] = "/api/v1/qr-sessions/" + str(item.qr_session_id)
        return _dto(item)
    except Exception as exc: raise to_http_exception(exc)

@router.get("/api/v1/lessons/{lesson_id}/qr-sessions", response_model=List[QRSessionResponseDTO])
def list_qr_sessions(lesson_id: str, request: Request):
    try: return [_dto(x) for x in _service(request).list_for_lesson(lesson_id)]
    except Exception as exc: raise to_http_exception(exc)

@router.get("/api/v1/qr-sessions/{session_id}", response_model=QRSessionResponseDTO)
def get_qr_session(session_id: str, request: Request):
    try: return _dto(_service(request).get(session_id))
    except Exception as exc: raise to_http_exception(exc)

@router.delete("/api/v1/qr-sessions/{session_id}", status_code=204)
def close_qr_session(session_id: str, request: Request):
    try: _service(request).close(session_id); return Response(status_code=204)
    except Exception as exc: raise to_http_exception(exc)
