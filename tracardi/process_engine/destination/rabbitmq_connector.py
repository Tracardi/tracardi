from tracardi.process_engine.destination.connector import Connector


class RabbitMqConnector(Connector):

    async def run(self, mapping, delta):
        print(mapping, delta)


