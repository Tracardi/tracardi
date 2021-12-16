from pydantic import AnyHttpUrl

from tracardi.domain.entity import Entity


class TracardiProEndpoint(Entity):
    url: AnyHttpUrl
    token: str
    username: str
    password: str

    def get_registered_services_endpoint(self):
        return f"/services/{self.token}"

    def get_available_services_endpoint(self):
        return f"/services"
