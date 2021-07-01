from typing import Optional, Any

from pydantic import BaseModel


class PII(BaseModel):
    """
    Personally identifiable information, or PII, is any data that could
    potentially be used to identify a particular person. Examples include a full name,
    Social Security number, driver's license number, bank account number,
    passport number, and email address.
    """
    name: Optional[Any] = ''
    surname: Optional[Any] = ''
    birthDate: Optional[Any] = None
    email: Optional[Any] = ''
    telephone: Optional[Any] = ''
    other: Optional[dict] = {}

    def merge(self, pii: 'PII'):
        if isinstance(self.name, list):
            self.name.append(pii.name)
            self.name = list(set(self.name))
        else:
            self.name = list({self.name, pii.name}) if self.name else pii.name

        if isinstance(self.surname, list):
            self.surname.append(pii.surname)
            self.surname = list(set(self.surname))
        else:
            self.surname = list({self.surname, pii.surname}) if self.surname else pii.surname

        if isinstance(self.email, list):
            self.email.append(pii.email)
            self.email = list(set(self.email))
        else:
            self.email = list({self.email, pii.email}) if self.email else pii.email

        if isinstance(self.telephone, list):
            self.telephone.append(pii.telephone)
            self.telephone = list(set(self.telephone))
        else:
            self.telephone = list({self.telephone, pii.telephone}) if self.telephone else pii.telephone

        if isinstance(self.birthDate, list):
            self.birthDate.append(pii.birthDate)
            self.birthDate = list(set(self.birthDate))
        else:
            self.birthDate = list({self.birthDate, pii.birthDate}) if self.birthDate else pii.birthDate

        # todo add other
