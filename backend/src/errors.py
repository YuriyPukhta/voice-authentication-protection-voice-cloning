from fastapi import HTTPException
from starlette.responses import JSONResponse


class TranscriptionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class AudioProcessingError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class AuthRequestFailed(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)


class NotFound(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)


class BadRequest(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


ERRORS = [
    TranscriptionError, AudioProcessingError, AuthRequestFailed, NotFound
]


def add_error_handlers(app):
    for error in ERRORS:
        @app.exception_handler(error)
        async def transcription_exception_handler(_request, exc: error):
            return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})
