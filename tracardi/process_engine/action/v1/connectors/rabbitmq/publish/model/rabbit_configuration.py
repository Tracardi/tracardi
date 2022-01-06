from pydantic import BaseModel


class RabbitSourceConfiguration(BaseModel):
    uri: str = 'amqp://127.0.0.1:5672//'
    timeout: int = 5
    virtual_host: str = None
    port: int = None
