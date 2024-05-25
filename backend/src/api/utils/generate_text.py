from faker import Faker


def generate_random_sentence() -> str:
    fake = Faker()
    return fake.sentence()