from pydantic import BaseModel


class TrelloCredentials(BaseModel):
    api_key: str
    token: str

    @staticmethod
    def create():
        return TrelloCredentials(
            api_key="",
            token=""
        )
