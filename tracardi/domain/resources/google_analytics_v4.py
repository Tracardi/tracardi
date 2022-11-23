from pydantic import BaseModel


class GoogleAnalyticsV4Credentials(BaseModel):
    api_key: str
    measurement_id: str