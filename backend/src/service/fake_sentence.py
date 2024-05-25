from faker import Faker

fake = Faker()

def generate_random_sentence() -> str:
    return fake.sentence()