from typing import Optional
from pydantic import BaseModel


class PII(BaseModel):

    """
    Personally identifiable information, or PII, is any data that could
    potentially be used to identify a particular person. Examples include a full name,
    Social Security number, driver's license number, bank account number,
    passport number, and email address.
    """

    name: Optional[str] = None
    surname: Optional[str] = None
    birth_date: Optional[str] = None
    marital_status: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    whatsapp: Optional[str] = None
    other: Optional[dict] = {}

