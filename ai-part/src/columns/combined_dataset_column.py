from enum import Enum


class CombinedDatasetColumn(str, Enum):
    ANCHOR_ID = 'anchor_client_id'
    POSNEG_ID = 'posneg_client_id'
    ANCHOR_PATH = 'anchor_path'
    POSNEG_PATH = 'posneg_path'
    SOURCE_ANCHOR = 'anchor_source'
    SOURCE_POSNEG = 'posneg_source'
