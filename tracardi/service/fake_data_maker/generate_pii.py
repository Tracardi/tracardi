from random import randint

from faker import Faker
from faker.providers import internet, phone_number, credit_card

fake = Faker()
fake.add_provider(internet)
fake.add_provider(phone_number)
fake.add_provider(credit_card)

fake_emails = [fake.email() for _ in range(0, 1500)]


def make_fake_pii():
    name = fake.name().split()
    return {
        "firstname": name[0],
        "lastname": name[1],
        "phone": fake.phone_number(),
        "email": fake_emails[randint(0, 1499)]
    }


def make_identification_data():
    name = fake.name().split()
    tn = fake.phone_number()
    return {
        "firstname": name[0],
        "lastname": name[1],
        "name": name,
        "slack": f"@{name[1]}",
        "telegram": f"@{name[0]}",
        "phone": tn,
        "whatsapp": tn,
        "email": fake_emails[randint(0, 1499)],
        "birthday": fake.date_time_between(start_date='-75y', end_date='-18y').strftime("%Y-%m-%dT%H:%M:%S")
    }


fake_persons = [make_fake_pii() for _ in range(0, 500)]
fake_identity = [make_identification_data() for _ in range(0, 500)]


def make_fake_login():
    name = fake.name().split()
    return {
        "email": fake_emails[randint(0, 1499)]
    }


def make_fake_loc():
    lng, lat, town, country, tz = fake.local_latlng()
    return {
        "login": fake_emails[randint(0, 1499)],
        "lng": lng,
        "lat": lat,
        "town": town,
        "country": country,
        "tz": tz
    }
