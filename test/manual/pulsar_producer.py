import logging

import pulsar

from com_tracardi.service.tracking.queue.pulsar_topics import EVENT_TOPIC

pulsar_logger = logging.getLogger('pulsar')
pulsar_logger.setLevel(logging.DEBUG)

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.lkLZkhoRTS7S11iehntprBA13PjcdDCihanssiSaS0rAHZeJOsCcCKa1XIPZZHbv0SmYwmv4YTIKf7NMSzuI-J0iO9br5caJh_1L3LhUTlsbaWybh7sQPF2rFyEFXa68ojTccjXOk8lWVUg0p3An9q_MMb4jDYND3K89CxRQpwhCPWmF_9Cw4cZJM252NYtSMsVyCkRZsCgu1Zco9GePPlMBrE9MtYpTaIRUuD4MQrunjC9kjWIVgxCEM3wf7B-A8bU_0dDuD5g2WWCsJ_Z-_9T2ucQqglcatrGnsOC0zCmSzmbGDe4372eGo6aak-4kbL3CZ0QnS36Tuji8T1ucHw"
client = pulsar.Client(
    'pulsar://192.168.1.178:6650',
    authentication=pulsar.AuthenticationToken(token),
    connection_timeout_ms=6000,
    logger=pulsar_logger,
    listener_name='external'
)
prod = client.create_producer(EVENT_TOPIC)
for _ in range(0,10):
    prod.send("test".encode())
client.close()
