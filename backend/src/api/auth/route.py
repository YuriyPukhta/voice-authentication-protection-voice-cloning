from datetime import datetime, timedelta

import pytz
from fastapi import File, UploadFile, APIRouter, Depends, Security
from sqlalchemy.orm import Session

from src.api.auth.schemas import RecordSessionResponse, UserInput, AuthResponse, SessionUpdateResponse, CodeInputModel, \
    CodeResponse
from src.api.dependencies.auth import get_request_auth, get_request_session
from src.api.dependencies.db import get_db
from src.api.utils.compare_similarite import similar
from src.service.transcribe import get_text_from_speach
from src.config import AppConfig
from src.constant import CodeType
from src.errors import NotFound, AudioProcessingError, BadRequest, AuthRequestFailed
from src.models_db import RequestSession, RequestAuth
from src.repository_utils.code import get_code_by_code, add_code_record
from src.repository_utils.record import add_record, get_record_by_user_id
from src.repository_utils.requset_auth import add_request_register, add_request_session, update_request_session
from src.repository_utils.user import add_user, get_user_by_username, get_user_by_id
from src.service.fake_sentence import generate_random_sentence
from src.service.generated_id import generate_guid
from src.service.jwt_service import create_jwt_register, create_jwt_auth
from src.service.save_file import save_audio_locally
from src.service.voice_auth import validate

save_path = './file'

auth_router = APIRouter()
config = AppConfig()
@auth_router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), db: Session = Depends(get_db),  request: RequestSession = Security(get_request_session)):
    file_name = file.filename.split(".")[-1]
    if file_name != "wav":
        raise AudioProcessingError("Unsupported media type")

    if request.update_at > datetime.now(pytz.utc).replace(tzinfo=None) + timedelta(seconds=config.TIME_FOR_RECORD):
        raise AudioProcessingError("Current phrase. is expired")

    user = get_user_by_id(id=request.user_id, db=db)
    if user is None:
        raise BadRequest("Bad User")
    record = get_record_by_user_id(user_id=user.id, db=db)
    if record is None:
        raise BadRequest("Bad User")

    #text_from_record = await get_text_from_speach(file)
    #if similar(text_from_record, request) < config.SIMILARITY_LIMIT:
        #raise AuthRequestFailed("Recorded text dose not corresponded target")
    res = validate(record.path, file.file)
    if res < config.NEGATIVE_THRESHOLD:
        raise AuthRequestFailed("Current voice docent correspond target")
    code = add_code_record(user_id=user.id, db=db)
    return AuthResponse(
        code=code
        )

@auth_router.post("/register")
async def register(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        request: RequestAuth = Security(get_request_auth)
):
    file_name = file.filename.split(".")[-1]
    if file_name != "wav":
        AudioProcessingError("Unsupported media type")

    user = get_user_by_username(username=request.username, db=db)
    if user is not None:
        raise BadRequest("User already has record")

    file_name = str(generate_guid())
    file_path = await save_audio_locally(file, file_name)
    user = add_user(username=request.username, db=db)
    add_record(path=file_path, user_id=user.id, db=db)
    db.commit()


@auth_router.post("/request-register")
async def request_register(userInput: UserInput,  db: Session = Depends(get_db)):
    user = get_user_by_username(username=userInput.username, db=db)
    if(user is not None):
        raise BadRequest("User with this name already exits")
    request = add_request_register(generate_random_sentence(), username=userInput.username, db=db)
    return RecordSessionResponse(
        token=create_jwt_register(request.id),
        text=request.text,
        start_at=request.update_at,
        duration=config.TIME_FOR_RECORD
    )


@auth_router.post("/auth")
async def request_auth(userInput: UserInput, db: Session = Depends(get_db)):
    user = get_user_by_username(username=userInput.username, db=db)
    if(user is None):
        raise NotFound("User not Found")
    text = generate_random_sentence()
    session = add_request_session(text=text, user_id=user.id, db=db)
    return RecordSessionResponse(
        token=create_jwt_auth(session.id),
        text=session.text,
        start_at=session.update_at,
        duration=config.TIME_FOR_RECORD
    )

@auth_router.post("/update-session")
async def update(request=Security(get_request_session), db: Session = Depends(get_db)):
    text = generate_random_sentence()
    update_session = update_request_session(request, new_text=text, db=db)
    return SessionUpdateResponse(
        text=update_session.text,
        start_at=update_session.update_at,
        duration=config.TIME_FOR_RECORD
    )

@auth_router.post("/validate-code")
async def validate_code(code: CodeInputModel, db: Session = Depends(get_db)):
    code = get_code_by_code(code.code, db=db)
    if code is None or code.created_at + timedelta(minutes=config.CODE_VALID_IN_MINUTES) < datetime.utcnow():
        raise NotFound("Code not found")
    user = get_user_by_username(username=code.username, db=db)
    if user is None:
        raise NotFound("User is wrong")
    if code.user_id == user.id:
        response = CodeType.VALID
    else:
        response = CodeType.INVALID
    return CodeResponse(
        type=response
    )
