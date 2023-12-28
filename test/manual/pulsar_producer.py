import logging

import pulsar

from com_tracardi.service.tracking.queue.pulsar_topics import EVENT_TOPIC

pulsar_logger = logging.getLogger('pulsar')
pulsar_logger.setLevel(logging.DEBUG)

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.LXJZ6_MK7UvgBoP1hcst9_rboucY0KEHubgOtX-3aXk"
client = pulsar.Client(
    'pulsar://65.109.120.124:6650',
    authentication=pulsar.AuthenticationToken(token),
    connection_timeout_ms=1000,
    logger=pulsar_logger,
    listener_name='external'
)
prod = client.create_producer(EVENT_TOPIC)
for _ in range(0,10):
    prod.send("test".encode())
client.close()
