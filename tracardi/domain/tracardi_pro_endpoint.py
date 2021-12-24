from pydantic import AnyHttpUrl

from tracardi.domain.entity import Entity


class TracardiProEndpoint(Entity):
    url: AnyHttpUrl
    token: str
    username: str
    password: str

    def get_running_services_endpoint(self):
        return f"/services/{self.token}"

    def get_available_services_endpoint(self):
        return f"/services"

    def get_running_service(self, id):
        return f"/service/{id}"
