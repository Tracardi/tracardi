import logging

import pulsar

from com_tracardi.service.tracking.queue.pulsar_topics import EVENT_TOPIC

pulsar_logger = logging.getLogger('pulsar')
pulsar_logger.setLevel(logging.DEBUG)

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.OcONdDoPgl1eiC-lfXPLU5Fu4uEyzMLnsASw-HC9JOxST-sv8t9aZwMkGP0bqqy4r7Ln2QJSFe_IDiVeu6leB_37VD9tKB-cANsKZidSsrKTu5DzVS9XsEy0Gr5PR38mqLx6WPlUcNLh-SvyHHUrnaBDQUQfujOaz1Fr0LbHVbS5Wm9mOk_ZIALQEEJ6r2SRjCxe1DLP11K68-Ih0HTI3wSwMpaAGW3EE00AS5m0Yurx1FSr4JCjQ3tlmgkuEgpvxYPQfigmPvHGs95szdA1JbW6vjoT9b_wQIW00F8A3cLbmXtVeFNuyCQwToW35svPsDitExhd_-METouThhtZfg"
client = pulsar.Client(
    'pulsar://135.181.100.250:6650',
    authentication=pulsar.AuthenticationToken(token),
    connection_timeout_ms=1000,
    logger=pulsar_logger,
    listener_name='external'
)
consumer = client.subscribe(EVENT_TOPIC,
                        'test'
                        )

while True:
    msg = consumer.receive(timeout_millis=1000*10)  # Realising consumer every 15 min.
    payload = msg.data()
    print(payload)
    consumer.acknowledge(msg)

client.close()
