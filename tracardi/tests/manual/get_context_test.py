import asyncio
from pprint import pprint

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.storage.elastic import Elastic


async def main():
    payload = {
        "metadata": {
            "time": {
                "now": "2021-05-07T15:09:35.298Z",
                "utc": -2
            }
        },
        "source": {"id": "scope"},
        "event_server": {
            "browser": {
                "browser": {
                    "name": "Netscape",
                    "engine": "Gecko",
                    "appVersion": "5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
                    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
                    "language": "en-US",
                    "onLine": True,
                    "javaEnabled": False,
                    "cookieEnabled": True
                },
                "device": {
                    "platform": "Linux x86_64"
                }
            },
            "storage": {
                "local": {
                    "ajs_group_id": "null",
                    "ajs_user_id": "null",
                    "__user_id": "\"user-id\"",
                    "ajs_group_properties": "{}",
                    "ajs_user_traits": "{}",
                    "__anon_id": "\"ed964435-ea00-4f5a-86d3-89ca0accdeb5\"",
                    "ajs_anonymous_id": "\"6e6c0ef9-d736-4a03-a8fd-f884698481b7\"",
                    "debug": "undefined",
                    "__user_traits": "{\"a\":1}"
                },
                "cookie": {
                    "cookies1": "tracardi-session-id=9ec4500a-057e-4a05-b460-8f132e73ef63; ajs_group_id=null; ajs_anonymous_id=%226e6c0ef9-d736-4a03-a8fd-f884698481b7%22; ajs_user_id=%22f4ca124298%22; event_server-profile-id=32666cad-657b-494e-a7ef-ec28c349eae2",
                    "cookies2": "tracardi-session-id=9ec4500a-057e-4a05-b460-8f132e73ef63, ajs_group_id=null, ajs_anonymous_id=\"6e6c0ef9-d736-4a03-a8fd-f884698481b7\", ajs_user_id=\"f4ca124298\", event_server-profile-id=32666cad-657b-494e-a7ef-ec28c349eae2"
                }
            },
            "screen": {
                "width": 1920,
                "height": 1080,
                "innerWidth": 1745,
                "innerHeight": 237,
                "availWidth": 1920,
                "availHeight": 1053,
                "colorDepth": 24,
                "pixelDepth": 24
            }
        },
        "profile": {
            "id": "6ec4500a-057e-4a05-b460-8f132e73ef63"
        },
        "session": {
            "id": "6ec4500a-057e-4a05-b460-8f132e73ef63"
        },
        "events": [
            {
                "type": "sessionCreated"
            }
        ]
    }

    context = TrackerPayload(**payload)
    pprint(await context.collect())
    #
    await Elastic.instance().close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
