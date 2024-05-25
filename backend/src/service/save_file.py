import os

from pydub import AudioSegment
from io import BytesIO


async def save_audio_locally(file, name):
    try:
        audio = AudioSegment.from_file(BytesIO(await file.read()), format=file.filename.split(".")[-1])

        save_path = './file'

        complete_file_name = os.path.join(save_path, f"{name}.wav")
        audio.export(complete_file_name, format="wav")

        return complete_file_name
    except Exception as e:
        print("Error saving audio: {str(e)}")