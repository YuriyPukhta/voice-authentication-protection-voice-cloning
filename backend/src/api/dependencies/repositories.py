from fastapi import Depends

from backend.api.dependencies.db import DBClient, get_db
from backend.repository.appointment_repository import AppointmentRepository
from backend.repository.consent_repository import VeloxConsentRepository


def get_appointment_repository(db: DBClient = Depends(get_db)):
    return AppointmentRepository(db)


def get_consent_repository(db: DBClient = Depends(get_db)):
    return VeloxConsentRepository(db)
