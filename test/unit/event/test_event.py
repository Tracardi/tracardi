from pydantic import ValidationError

from tracardi.domain.event import Event


def test_event_data():
    data = {"id": "ef4f5ad3-3ad6-44c8-9963-51d2c4c26f22", "name": "Profile Update", "metadata": {"aux": {}, "time": {
        "insert": "2023-06-18 21:40:35.347516", "create": None, "update": None, "process_time": 0}, "ip": None,
                                                                                                 "status": "collected",
                                                                                                 "channel": "System",
                                                                                                 "processed_by": {
                                                                                                     "rules": [],
                                                                                                     "flows": [],
                                                                                                     "third_party": []},
                                                                                                 "profile_less": False,
                                                                                                 "debug": False,
                                                                                                 "valid": True,
                                                                                                 "error": False,
                                                                                                 "warning": False,
                                                                                                 "instance": {
                                                                                                     "id": "b9d6d1f3-b9b2-47f9-8dcd-5257497afc32"}},
            "type": "profile-update",
            "device": {"name": "Other", "brand": "Gross and Sons", "model": "attention win customer", "type": None,
                       "touch": False, "ip": None, "resolution": None,
                       "geo": {"country": {"name": "America/Chicago", "code": "US"}, "city": "Muskogee", "county": "US",
                               "postal": None, "latitude": 35.74788, "longitude": -95.36969}, "color_depth": None,
                       "orientation": None}, "os": {"name": "Windows", "version": "NT"},
            "app": {"type": None, "name": None, "version": None, "language": "ml_IN", "bot": False, "resolution": None},
            "hit": {"name": None, "url": None, "referer": None, "query": None, "category": None},
            "utm": {"source": None, "medium": None, "campaign": None, "term": None, "content": None},
            "properties": {"pii": {"education": {}, "civil": {}, "attributes": {}},
                           "contact": {"app": {}, "address": {}}, "media": {"social": {}}, "job": {"company": {}},
                           "preferences": {}, "loyalty": {"card": {}}}, "traits": {},
            "operation": {"new": True, "update": False},
            "source": {"id": "778ded05-4ff3-4e08-9a86-72c0195fa95d", "type": ["internal"],
                       "bridge": {"id": "778ded05-4ff3-4e08-9a86-72c0195fa95d", "name": "REST API Bridge"},
                       "timestamp": "2023-06-18 21:40:35.329523", "name": "Test random data",
                       "description": "Internal event source for random data.", "channel": "System", "enabled": True,
                       "transitional": False, "tags": ["internal"], "groups": ["Internal"], "returns_profile": False,
                       "permanent_profile_id": False, "requires_consent": False, "manual": None, "locked": False,
                       "synchronize_profiles": True, "config": None},
            "session": {"id": "f66e7c2e-3e7f-48c3-b606-0fe7a9f40f86", "start": "2023-06-18 21:40:35.352506",
                        "duration": 0.0, "tz": "Africa/Maputo"},
            "profile": {"id": "5f1e670b-994c-49b6-af97-c0af9fd036b9"}, "context": {}, "request": {}, "config": {},
            "tags": {"values": [], "count": 0}, "aux": {},
            "data": {
                "pii": {"firstname": "Jessica", "lastname": "Carlson", "name": "Jessica Carlson",
                        "birthday": "1977-06-14 18:56:42", "language": {"native": None, "spoken": None},
                        "gender": "female",
                        "education": {"level": "Technical Education"}, "civil": {"status": "Married"},
                        "attributes": {"height": 178, "weight": 78, "shoe_number": 43}},
                "contact": {"email": None, "phone": None,
                            "app": {"whatsapp": "(810)199-2432", "discord": None, "slack": "@Carlson",
                                    "twitter": "@tracardi", "telegram": "@Jessica", "wechat": None, "viber": None,
                                    "signal": None, "other": {}},
                            "address": {"town": "Osbornemouth", "county": None, "country": "Mayotte",
                                        "postcode": "59989",
                                        "street": "53975 Charles Grove Apt. 278", "other": None}, "confirmations": []},
                "identifier": {"id": None, "badge": None, "passport": None, "credit_card": None, "token": None},
                "media": {"image": "http://tracardi.com/demo/image/female/profile_27.JPG",
                          "webpage": "http://www.tracardi.com",
                          "social": {"twitter": "@tracardi", "facebook": "tracardi", "youtube": "@tracardi",
                                     "instagram": None, "tiktok": None, "linkedin": None, "reddit": None, "other": {}}},
                "preferences": {
                    "purchases": None, "colors": "gray", "sizes": "m", "devices": "tablet",
                    "channels": ["mobile"], "payments": None, "brands": "Müller",
                    "fragrances": "Issey Miyake", "services": "Fitness and Wellness",
                    "other": []}, "job": {"position": "Event Planner", "salary": 4139, "type": None,
                                          "company": {"name": "Best Buy", "size": 183, "segment": "Healthcare",
                                                      "country": "Brazil"}, "department": "Public Relations"},
                "loyalty": {"codes": "free2",
                            "card": {"id": None, "name": None, "issuer": "Vans", "expires": "2024-02-29 20:08:31",
                                     "points": 45}}}}
    try:
        event = Event(**data)
    except ValidationError as e:
        assert False, f"Raised an exception {e}"
