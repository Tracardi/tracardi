import aiohttp
from fastapi import HTTPException


class TrelloClient:

    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token

    async def get_list_id(self, board_url: str, list_name: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f'https://api.trello.com/1/members/me/boards?key={self.api_key}&token={self.token}'
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                boards = list(filter(lambda x: x["url"] == board_url, await response.json()))
                if not boards:
                    raise ValueError("Given board does not exist")

            async with session.get(
                    url=f'https://api.trello.com/1/boards/{boards.pop()["id"]}/lists?'
                        f'key={self.api_key}&token={self.token}'
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                lists = list(filter(lambda x: x["name"] == list_name, await response.json()))
                if not lists:
                    raise ValueError("Given list does not exist.")
                return lists.pop()["id"]

    async def add_card(self, list_id: str, **kwargs) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"https://api.trello.com/1/cards?key={self.api_key}&token={self.token}",
                params={
                    "idList": list_id
                },
                data={key: val for key, val in kwargs.items() if val is not None}
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                return await response.json()

    async def delete_card(self, list_id: str, card_name: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"https://api.trello.com/1/lists/{list_id}/cards?key={self.api_key}&token={self.token}"
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                cards = list(filter(lambda x: x["name"] == card_name, await response.json()))
                if not cards:
                    raise ValueError("Given card does not exist.")
                card_id = cards.pop()["id"]

            async with session.delete(
                url=f"https://api.trello.com/1/cards/{card_id}?key={self.api_key}&token={self.token}"
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                return await response.json()

    async def move_card(self, current_list_id: str, list_id: str, card_name: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f"https://api.trello.com/1/lists/{current_list_id}/cards?key={self.api_key}&token={self.token}"
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                cards = list(filter(lambda x: x["name"] == card_name, await response.json()))
                if not cards:
                    raise ValueError("Given card does not exist.")
                card_id = cards.pop()["id"]

            async with session.put(
                url=f"https://api.trello.com/1/cards/{card_id}?key={self.api_key}&token={self.token}",
                data={
                    "idList": list_id
                }
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                return await response.json()

    async def add_member(self, list_id: str, card_name: str, member_id: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"https://api.trello.com/1/lists/{list_id}/cards?key={self.api_key}&token={self.token}"
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                cards = list(filter(lambda x: x["name"] == card_name, await response.json()))
                if not cards:
                    raise ValueError("Given card does not exist.")
                card_id = cards.pop()["id"]

            async with session.put(
                url=f"https://api.trello.com/1/cards/{card_id}/idMembers?key={self.api_key}&token={self.token}",
                data={
                    "value": member_id
                }
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=response.content)
                return await response.json()
