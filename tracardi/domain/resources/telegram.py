from pydantic import field_validator, BaseModel


class TelegramResource(BaseModel):
    bot_token: str
    chat_id: int

    @field_validator("bot_token")
    @classmethod
    def bot_token_must_not_be_empty(cls, value):
        value = value.strip()
        if len(value) < 1:
            raise ValueError("Bot token can not be empty.")
        return value
