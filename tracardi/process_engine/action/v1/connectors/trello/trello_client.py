from tracardi.service.tracardi_http_client import HttpClient


class TrelloClient:

    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def get_list_id(self, board_url: str, list_name: str) -> str:
        url = f'https://api.trello.com/1/members/me/boards?key={self.api_key}&token={self.token}'
        async with HttpClient(self.retries) as client:
            async with client.get(
                    url=url
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response from Trello with status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                boards = list(filter(lambda x: x["url"] == board_url, result))
                if not boards:
                    raise ValueError(f"The board URL {board_url} does not exist in Trello.")

            async with client.get(
                    url=f'https://api.trello.com/1/boards/{boards.pop()["id"]}/lists?'
                        f'key={self.api_key}&token={self.token}'
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response from Trello with status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                lists = list(filter(lambda x: x["name"] == list_name, result))
                if not lists:
                    raise ValueError(f"List {list_name} does not exist in Trello.")
                return lists.pop()["id"]

    async def add_card(self, list_id: str, **kwargs) -> dict:

        async with HttpClient(self.retries) as client:
            async with client.post(
                    url=f"https://api.trello.com/1/cards?key={self.api_key}&token={self.token}",
                    params={
                        "idList": list_id
                    },
                    data={key: val for key, val in kwargs.items() if val is not None}
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                return result

    async def delete_card(self, list_id: str, card_name: str) -> dict:
        async with HttpClient(self.retries) as client:
            async with client.get(
                    url=f"https://api.trello.com/1/lists/{list_id}/cards?key={self.api_key}&token={self.token}"
            ) as response:

                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                cards = list(filter(lambda x: x["name"] == card_name, result))

                if not cards:
                    raise ValueError("Given card does not exist.")

                card_id = cards.pop()["id"]

            async with client.delete(
                    url=f"https://api.trello.com/1/cards/{card_id}?key={self.api_key}&token={self.token}"
            ) as response:

                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                return result

    async def move_card(self, current_list_id: str, list_id: str, card_name: str) -> dict:
        async with HttpClient(self.retries) as client:
            async with client.get(
                    url=f"https://api.trello.com/1/lists/{current_list_id}/cards?key={self.api_key}&token={self.token}"
            ) as response:

                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                cards = list(filter(lambda x: x["name"] == card_name, result))

                if not cards:
                    raise ValueError("Given card does not exist.")

                card_id = cards.pop()["id"]

            async with client.put(
                    url=f"https://api.trello.com/1/cards/{card_id}?key={self.api_key}&token={self.token}",
                    data={
                        "idList": list_id
                    }
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                return result

    async def add_member(self, list_id: str, card_name: str, member_id: str) -> dict:
        async with HttpClient(self.retries) as client:
            async with client.get(
                    url=f"https://api.trello.com/1/lists/{list_id}/cards?key={self.api_key}&token={self.token}"
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                cards = list(filter(lambda x: x["name"] == card_name, result))
                if not cards:
                    raise ValueError("Given card does not exist.")

                card_id = cards.pop()["id"]

            async with client.put(
                    url=f"https://api.trello.com/1/cards/{card_id}/idMembers?key={self.api_key}&token={self.token}",
                    data={
                        "value": member_id
                    }
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {} "
                                          "with message {}".format(response.status,
                                                                   result))

                return result
