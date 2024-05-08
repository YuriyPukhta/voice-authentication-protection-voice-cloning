from enum import Enum


class CombinedTripletDatasetColumn(str, Enum):
    ANCHOR_ID = 'anchor_client_id'
    POS_ID = 'pos_client_id'
    NEG_ID = 'neg_client_id'
    ANCHOR_PATH = 'anchor_path'
    POS_PATH = 'pos_path'
    NEG_PATH = 'neg_path'
    SOURCE_ANCHOR = 'anchor_source'
    SOURCE_POS = 'pos_source'
    SOURCE_NEG = 'neg_source'