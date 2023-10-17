import datetime

from tracardi.domain.profile import Profile, CustomMetric


def test_profile_must_have_id_in_ids():
    profile = Profile(id="1")
    assert profile.id in profile.ids


def test_next_metric_computation_date():
    p = Profile(id="1")
    assert p.get_next_metric_computation_date() is None
    next1 = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
    p.data.metrics.custom['metric1'] = dict(
        timestamp=datetime.datetime.utcnow(),
        next=next1,
        value=10
    )
    assert p.get_next_metric_computation_date() == next1

    next2 = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
    p.data.metrics.custom['metric2'] = dict(
        timestamp=datetime.datetime.utcnow(),
        next=next2,
        value=11
    )
    assert p.get_next_metric_computation_date() == next2

    next3 = datetime.datetime.utcnow() + datetime.timedelta(seconds=15)
    p.data.metrics.custom['metric3'] = dict(
        timestamp=datetime.datetime.utcnow(),
        next=next3,
        value=12
    )
    assert p.get_next_metric_computation_date() == next2


def test_has_metric():
    p = Profile(id="1")
    assert p.has_metric('metric1') is False
    next1 = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
    p.data.metrics.custom['metric1'] = dict(
        timestamp=datetime.datetime.utcnow(),
        next=next1,
        value=10
    )
    assert p.has_metric('metric1')


def test_needs_metric_computation():
    p = Profile(id="1")

    assert p.need_metric_computation('metric1') is False

    # After

    next1 = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
    p.data.metrics.custom['metric1'] = dict(
        timestamp=datetime.datetime.utcnow(),
        next=next1,
        value=10
    )

    assert p.need_metric_computation('metric1') is False

    # Before

    next1 = datetime.datetime.utcnow() + datetime.timedelta(seconds=-10)
    p.data.metrics.custom['metric1'] = dict(
        timestamp=datetime.datetime.utcnow(),
        next=next1,
        value=10
    )

    assert p.need_metric_computation('metric1') is True


def test_data_fill():
    data = {"id": "7743b7c7-4fd2-494b-8559-4244927f1a84", "ids": ["7743b7c7-4fd2-494b-8559-4244927f1a84"], "metadata": {
        "time": {"insert": datetime.datetime(2023, 6, 11, 22, 25, 13, 131541), "create": None,
                 "update": datetime.datetime(2023, 6, 11, 22, 40, 26, 122244),
                 "visit": {"last": None, "current": datetime.datetime(2023, 6, 11, 22, 25, 13, 133495), "count": 1,
                           "tz": None}}, "aux": {}},
            "operation": {"new": False, "update": False, "segment": False, "merge": []},
            "stats": {"visits": 0, "views": 0, "counters": {}}, "traits": {},
            "segments": [],
            "interests": {}, "consents": {}, "active": True, "aux": {},
            "data": {
                "pii": {
                    "firstname": None,
                    "lastname": "string",
                    "name": "string",
                    "birthday": datetime.datetime(2010, 1, 1, 0, 0),
                    "language": {"native": "string",
                                 "spoken": ["string"]},
                    "gender": "string",
                    "education": {"level": "string"},
                    "civil": {"status": "string"},
                    "attributes": {
                        "height": 0.0,
                        "weight": 0.0,
                        "shoe_number": 0.7}},
                "contact": {"email": None, "phone": "string",
                            "app": {"whatsapp": "string", "discord": "string", "slack": "string", "twitter": "string",
                                    "telegram": "string", "wechat": "string", "viber": "string", "signal": "string",
                                    "other": {}},
                            "address": {"town": "string", "county": "string", "country": "string", "postcode": "string",
                                        "street": "string", "other": "string"}, "confirmations": []},
                "identifier": {"id": None, "badge": None, "passport": None, "credit_card": None, "token": None},
                "devices": {"names": [], "last": {
                    "geo": {"country": {"name": None, "code": None}, "city": None, "county": None, "postal": None,
                            "latitude": None, "longitude": None}}}, "media": {"image": "string", "webpage": "string",
                                                                              "social": {"twitter": "string",
                                                                                         "facebook": "string",
                                                                                         "youtube": "string",
                                                                                         "instagram": "string",
                                                                                         "tiktok": "string",
                                                                                         "linkedin": "string",
                                                                                         "reddit": "string",
                                                                                         "other": {}}},
                "preferences": {"purchases": ["string"], "colors": ["string"], "sizes": ["string"],
                                "devices": ["string"], "channels": ["string"], "payments": ["string"],
                                "brands": ["string"], "fragrances": ["string"], "services": ["string"],
                                "other": ["string"]}, "job": {"position": "string", "salary": 10.0, "type": "string",
                                                              "company": {"name": "string", "size": 100,
                                                                          "segment": None,
                                                                          "country": "string"}, "department": "string"},
                "metrics": {"ltv": None}, "loyalty": {"codes": ["string"],
                                                      "card": {"id": "string", "name": "string", "issuer": "string",
                                                               "expires": datetime.datetime(2022, 1, 1, 0, 0),
                                                               "points": 0.0}}}}

    Profile(**data)
