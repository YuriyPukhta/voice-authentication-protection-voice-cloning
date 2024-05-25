from fastapi import UploadFile
from pydub import AudioSegment
from io import BytesIO

from src.errors import AudioProcessingError

import speech_recognition as sr

from src.errors import TranscriptionError


def transcribe_speach(
    wav_io: BytesIO
):
    recognizer = sr.Recognizer()
    audio_data = sr.AudioFile(wav_io)

    with audio_data as source:
        audio_content = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_content)
        return text
    except sr.UnknownValueError:
        raise TranscriptionError("Could not understand the audio")
    except sr.RequestError as e:
        raise TranscriptionError(f"Could not request results; {e}")


async def get_text_from_speach(file: UploadFile):
    file_name = file.filename.split(".")[-1]
    data = BytesIO(await file.read())
    if file_name == "wav":
        audio = AudioSegment.from_file(data, format=file_name)
    else:
        AudioProcessingError("Unsupported media type")
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return transcribe_speach(wav_io)
