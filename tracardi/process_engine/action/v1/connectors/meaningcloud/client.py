import aiohttp
from fastapi import HTTPException


class MeaningCloudClient:

    def __init__(self, token: str):
        self._token = token

    async def deep_categorization(self, txt: str, model: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://api.meaningcloud.com/deepcategorization-1.0",
                data={
                    "key": self._token,
                    "txt": txt,
                    "model": model
                }
            ) as response:

                if response.status != 200 or (await response.json()).get("status", {"code": "1"})["code"] != "0":
                    raise HTTPException(status_code=response.status, detail=response.content)

                return await response.json()

    async def topics_extraction(self, txt: str, lang: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://api.meaningcloud.com/topics-2.0",
                data={
                    "key": self._token,
                    "txt": txt,
                    "lang": lang,
                    "tt": "a"
                }
            ) as response:

                if response.status != 200 or (await response.json()).get("status", {"code": "1"})["code"] != "0":
                    raise HTTPException(status_code=response.status, detail=response.content)

                return await response.json()

    async def corporate_reputation(self, txt: str, lang: str, relaxed_typography: bool, focus: str = None,
                                   company_type: str = None):
        data = {
            "key": self._token,
            "txt": txt,
            "lang": lang,
            "rt": "y" if relaxed_typography else "n"
        }

        if focus is not None:
            data["focus"] = focus
        if company_type is not None:
            data["filter"] = company_type

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://api.meaningcloud.com/reputation-2.0",
                data=data
            ) as response:

                if response.status != 200 or (await response.json()).get("status", {"code": "1"})["code"] != 0:
                    raise HTTPException(status_code=response.status, detail=response.content)

                return await response.json()

    async def summarize(self, txt: str, lang: str, sentences: int):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://api.meaningcloud.com/summarization-1.0",
                data={
                    "key": self._token,
                    "txt": txt,
                    "lang": lang,
                    "sentences": sentences
                }
            ) as response:

                if response.status != 200 or (await response.json()).get("status", {"code": "1"})["code"] != '0':
                    raise HTTPException(status_code=response.status, detail=response.content)

                return await response.json()
