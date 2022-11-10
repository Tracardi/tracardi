from pydantic import BaseModel


class GoogleAnalyticsCredentials(BaseModel):
    google_analytics_id: str