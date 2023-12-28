import logging

import pulsar

from com_tracardi.service.tracking.queue.pulsar_topics import EVENT_TOPIC

pulsar_logger = logging.getLogger('pulsar')
pulsar_logger.setLevel(logging.DEBUG)

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.LXJZ6_MK7UvgBoP1hcst9_rboucY0KEHubgOtX-3aXk'
client = pulsar.Client(
    'pulsar://65.109.120.124:6650',
    authentication=pulsar.AuthenticationToken(token),
    connection_timeout_ms=1000,
    logger=pulsar_logger
)
consumer = client.subscribe(EVENT_TOPIC,
                        'test'
                        )

while True:
    msg = consumer.receive(timeout_millis=1000)  # Realising consumer every 15 min.
    payload = msg.data()
    print(payload)
    consumer.acknowledge(msg)

client.close()
