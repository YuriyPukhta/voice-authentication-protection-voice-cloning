from enum import Enum


class DataFrameColumn(str, Enum):
    path = "path"
    client_id = "client_id"
    sentence = "sentence"
    generated_sentence = "generated_sentence"
    generated_path = "generated_path"
