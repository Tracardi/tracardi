import asyncio
from faker import Faker

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.track_event import track_event

from tracardi.service.fake_data_maker.generate_payload import generate_payload

source = "@test-source"

fake = Faker()
print(fake.date_time_between(start_date='-75y', end_date='-18y').strftime("%Y-%m-%d"))
payload = generate_payload(source)
payload = TrackerPayload(**payload)

asyncio.run(track_event(payload, '0.0.0.0', ['rest']))
print(payload.events)
# d = {
#       "pii": {
#         "firstname": "string",
#         "lastname": "string",
#         "name": "string",
#         "birthday": "date",
#         "language": "string",
#         "gender": "string",
#         "education": {
#           "level": "string"
#         },
#         "civil": {
#           "status": "string"
#         },
#         "attributes": {
#           "height": 0.0,
#           "weight": 0.0,
#           "shoe_number": 0.0
#         }
#       },
#       "contact": {
#         "email": "string",
#         "phone": "string",
#         "app": {
#           "whatsapp": "string",
#           "discord": "string",
#           "slack": "string",
#           "twitter": "string",
#           "telegram": "string",
#           "wechat": "string",
#           "viber": "string",
#           "signal": "string"
#         },
#         "address": {
#           "town": "string",
#           "county": "string",
#           "country": "string",
#           "postcode": "string",
#           "street": "string",
#           "other": "string"
#         }
#       },
#       "media": {
#         "image": "string",
#         "webpage": "string",
#         "social": {
#           "twitter": "string",
#           "facebook": "string",
#           "youtube": "string",
#           "instagram": "string",
#           "tiktok": "string",
#           "linkedin": "string",
#           "reddit": "string"
#         }
#       },
#       "job": {
#         "position": "string",
#         "salary": "string",
#         "type": "string",
#         "company": {
#           "name": "string",
#           "size": "string",
#           "segment": "string",
#           "country": "string"
#         },
#         "department": "string"
#       },
# "preferences": {
#         "purchases": "string",
#         "colors": "string",
#         "sizes": "string",
#         "devices": "string",
#         "channels": "string",
#         "payments": "string",
#         "brands": "string",
#         "fragrances": "string",
#         "services": "string",
#         "other": "string"
#       },
#       "loyalty": {
#         "codes": [],
#         "card": {
#           "id": "string",
#           "name": "string",
#           "issuer": "string",
#           "expires": "string",
#           "points": 0
#         }
#       }
#     }

# def print_dict_as_dot_notation(dictionary, prefix=''):
#     for key, value in dictionary.items():
#         if isinstance(value, dict):
#             print_dict_as_dot_notation(value, prefix + key + '.')
#         else:
#             xxx = prefix + key
#             # print(f"\"data.{xxx}\": [ \"traits.{xxx}\", \"equal\"],")
#             print(f"\"{xxx}\": \"{xxx}\",")
#
# print_dict_as_dot_notation(d)