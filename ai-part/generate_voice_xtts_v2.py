import os
import pandas as pd
from enum import Enum
from TTS.api import TTS

device = "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)

class DataFrameColumn(str, Enum):
    path = "path"
    client_id = "client_id"
    sentence = "sentence"
    generated_sentence = "generated_sentence"
    generated_path = "generated_path"


data_directory = "your_source_folder"
source_folder = data_directory + "/data/validated"
generated_folder = data_directory + "/data/generated"
generated_voice_tsv = data_directory + "/data/generated.tsv"
tsv_file_path = generated_voice_tsv
df = pd.read_csv(tsv_file_path, sep='\t')

for _, row in df.iterrows():
    generated_sentence = row[DataFrameColumn.generated_sentence]
    source_voice = f"{source_folder}/{row[DataFrameColumn.path]}"
    generated_voice = f"{generated_folder}/{row[DataFrameColumn.generated_path]}"
    if not os.path.exists(generated_voice):
        try:
            tts.tts_to_file(text=generated_sentence,
                            speaker_wav=source_voice, language="en", file_path=generated_voice)
        except Exception as exc:
            print(f"Error while voice generation: row with error {str(exc)}")
    else:
        print(f"Already generate: {generated_voice} ")
