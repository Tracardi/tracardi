from tracardi.domain.profile import Profile
from tracardi.process_engine.destination.connector import Connector


class RabbitMqConnector(Connector):

    def run(self, profile: Profile):
        pass
