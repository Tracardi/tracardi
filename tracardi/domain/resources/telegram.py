from pydantic import BaseModel, validator


class TelegramResource(BaseModel):
    bot_token: str
    chat_id: int

    @validator("bot_token")
    def bot_token_must_not_be_empty(cls, value):
        value = value.strip()
        if len(value) < 1:
            raise ValueError("Bot token can not be empty.")
        return value
