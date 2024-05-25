import uuid
import random


def generate_guid() -> str:
    return str(uuid.uuid4())

def generate_random_six_digit_number() -> int:
    return random.randint(100000, 999999)
