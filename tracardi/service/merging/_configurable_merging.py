from pydantic import BaseModel

from tracardi.process_engine.tql.utils.dictonary import flatten

class FieldMerger(BaseModel):
    method: str
    type: str
    default: str
    on_error: str

class A(BaseModel):

    bb: str

    def get_mergeble_fields(self):
        return [
            FieldMerger(method="a", type= 'b', default="b", on_error= '1')
        ]

class X(BaseModel):

    a: A

    def get_mergeble_fields(self):
        return [self.a]


x= X(a=A(bb="1"))

for _x in x.get_mergeble_fields():
    print(_x)

exit()
NEWER = 'newer'
OLDER = 'older'
APPEND = 'append'
ADD = 'add'
SUBSTRACT = 'substract'
BIGGER = 'bigger'
LOWER = 'lower'

NUMBER = 'number'
DATE = 'date'

DEFAULT = 'default'
ORIGIN = 'origin'
DESTINATION = 'destination'

strategy = {
    "data.loyalty.card.points": {
        "method": ADD,
        "type": NUMBER,
        "default": 0,
        "on_error": ORIGIN
    },
    "data.loyalty.card.expires": {
        "method": NEWER,
        "type": DATE,
        "default": None,
        "on_error": ORIGIN
    },
    "data.loyalty.card.issuer": {},
    "data.loyalty.card.name": {},
    "data.loyalty.card.id": {},
    "data.loyalty.codes": {},
    "data.metrics.next": {},
    "data.metrics.ltcocv": {},
    "data.metrics.ltcosv": {},
    "data.metrics.ltcop": {},
    "data.metrics.ltcocc": {},
    "data.metrics.ltcosc": {},
    "data.metrics.ltv": {},
    "data.job.department": {},
    "data.job.company.country": {},
    "data.job.company.segment": {},
    "data.job.company.size": {},
    "data.job.company.name": {},
    "data.job.type": {},
    "data.job.salary": {},
    "data.job.position": {},
    "data.preferences.other": {},
    "data.preferences.services": {},
    "data.preferences.fragrances": {},
    "data.preferences.brands": {},
    "data.preferences.payments": {},
    "data.preferences.channels": {},
    "data.preferences.devices": {},
    "data.preferences.sizes": {},
    "data.preferences.colors": {},
    "data.preferences.purchases": {},
    "data.media.social.reddit": {},
    "data.media.social.linkedin": {},
    "data.media.social.tiktok": {},
    "data.media.social.instagram": {},
    "data.media.social.youtube": {},
    "data.media.social.facebook": {},
    "data.media.social.twitter": {},
    "data.media.webpage": {},
    "data.media.image": {},
    "data.devices.last.geo.location": {},
    "data.devices.last.geo.longitude": {},
    "data.devices.last.geo.latitude": {},
    "data.devices.last.geo.postal": {},
    "data.devices.last.geo.county": {},
    "data.devices.last.geo.city": {},
    "data.devices.last.geo.country.code": {},
    "data.devices.last.geo.country.name": {},
    "data.devices.other": {},
    "data.devices.push": {},
    "data.identifier.coupons": {},
    "data.identifier.token": {},
    "data.identifier.credit_card": {},
    "data.identifier.passport": {},
    "data.identifier.badge": {},
    "data.identifier.id": {},
    "data.contact.confirmations": {},
    "data.contact.address.other": {},
    "data.contact.address.street": {},
    "data.contact.address.postcode": {},
    "data.contact.address.country": {},
    "data.contact.address.county": {},
    "data.contact.address.town": {},
    "data.contact.app.signal": {},
    "data.contact.app.viber": {},
    "data.contact.app.wechat": {},
    "data.contact.app.telegram": {},
    "data.contact.app.twitter": {},
    "data.contact.app.slack": {},
    "data.contact.app.discord": {},
    "data.contact.app.whatsapp": {},
    "data.contact.phone.whatsapp": {},
    "data.contact.phone.mobile": {},
    "data.contact.phone.business": {},
    "data.contact.phone.main": {},
    "data.contact.email.business": {},
    "data.contact.email.private": {},
    "data.contact.email.main": {},
    "data.pii.attributes.shoe_number": {},
    "data.pii.attributes.weight": {},
    "data.pii.attributes.height": {},
    "data.pii.civil.status": {},
    "data.pii.education.level": {},
    "data.pii.gender": {},
    "data.pii.language.spoken": {},
    "data.pii.language.native": {},
    "data.pii.birthday": {},
    "data.pii.display_name": {},
    "data.pii.lastname": {},
    "data.pii.firstname": {},
    "data.anonymous": {},
    "active": {},
    "segments": {},
    "stats.views": {},
    "stats.visits": {},
    "metadata.system.aux.auto_merge": {},
    "metadata.fields.data.contact.email.main": {},
    "metadata.status": {},
    "metadata.time.visit.tz": {},
    "metadata.time.visit.count": {},
    "metadata.time.visit.current": {},
    "metadata.time.visit.last": {},
    "metadata.time.segmentation": {},
    "metadata.time.update": {},
    "metadata.time.create": {},
    "metadata.time.insert": {},
    "ids": {},
    "id": {},
}

p = {
    "id": "e75a77f9-d4de-43ec-81a4-7478ec7dc69b",
    "ids": [
        "emm-58a3d72d-4219-fd3a-3479-df9f2a8c3d85",
        "e75a77f9-d4de-43ec-81a4-7478ec7dc69b"
    ],
    "metadata": {
        "time": {
            "insert": "2024-01-14T11:05:30.259437+00:00",
            "create": "2024-01-14T11:05:30.259437+00:00",
            "update": "2024-01-14T11:05:30.285791+00:00",
            "segmentation": None,
            "visit": {
                "last": None,
                "current": "2024-01-14T11:05:30.259998+00:00",
                "count": 1,
                "tz": None
            }
        },
        "aux": {},
        "status": None,
        "fields": {
            "data.contact.email.main": [
                "2024-01-14 11:05:30.261568+00:00",
                "c781b625-0026-4221-8af0-0839768dd97a"
            ]
        },
        "system": {
            "integrations": {},
            "aux": {
                "auto_merge": [
                    "data.contact.email.main"
                ]
            }
        }
    },
    "stats": {
        "visits": 0,
        "views": 0,
        "counters": {}
    },
    "traits": {},
    "segments": [],
    "interests": {},
    "consents": {},
    "active": True,
    "aux": {
        "geo": {}
    },
    "data": {
        "anonymous": False,
        "pii": {
            "firstname": None,
            "lastname": None,
            "display_name": None,
            "birthday": None,
            "language": {
                "native": None,
                "spoken": None
            },
            "gender": None,
            "education": {
                "level": None
            },
            "civil": {
                "status": None
            },
            "attributes": {
                "height": None,
                "weight": None,
                "shoe_number": None
            }
        },
        "contact": {
            "email": {
                "main": "sam456@example.com",
                "private": None,
                "business": None
            },
            "phone": {
                "main": None,
                "business": None,
                "mobile": None,
                "whatsapp": None
            },
            "app": {
                "whatsapp": None,
                "discord": None,
                "slack": None,
                "twitter": None,
                "telegram": None,
                "wechat": None,
                "viber": None,
                "signal": None,
                "other": {}
            },
            "address": {
                "town": None,
                "county": None,
                "country": None,
                "postcode": None,
                "street": None,
                "other": None
            },
            "confirmations": []
        },
        "identifier": {
            "id": None,
            "badge": None,
            "passport": None,
            "credit_card": None,
            "token": None,
            "coupons": None
        },
        "devices": {
            "push": [],
            "other": [],
            "last": {
                "geo": {
                    "country": {
                        "name": None,
                        "code": None
                    },
                    "city": None,
                    "county": None,
                    "postal": None,
                    "latitude": None,
                    "longitude": None,
                    "location": None
                }
            }
        },
        "media": {
            "image": None,
            "webpage": None,
            "social": {
                "twitter": None,
                "facebook": None,
                "youtube": None,
                "instagram": None,
                "tiktok": None,
                "linkedin": None,
                "reddit": None,
                "other": {}
            }
        },
        "preferences": {
            "purchases": [],
            "colors": [],
            "sizes": [],
            "devices": [],
            "channels": [],
            "payments": [],
            "brands": [],
            "fragrances": [],
            "services": [],
            "other": []
        },
        "job": {
            "position": None,
            "salary": None,
            "type": None,
            "company": {
                "name": None,
                "size": None,
                "segment": None,
                "country": None
            },
            "department": None
        },
        "metrics": {
            "ltv": 0,
            "ltcosc": 0,
            "ltcocc": 0,
            "ltcop": 0,
            "ltcosv": 0,
            "ltcocv": 0,
            "next": None,
            "custom": {}
        },
        "loyalty": {
            "codes": [],
            "card": {
                "id": None,
                "name": None,
                "issuer": None,
                "expires": None,
                "points": 0
            }
        }
    }
}

fp = flatten(p)

for x in fp:
    print(f"\"{x}\": {{}},")
