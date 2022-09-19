import os, sys
_local_dir = os.path.dirname(__file__)
sys.path.append(f"{_local_dir}/../proto/stubs")

import grpc
import tracardi.process_engine.action.v1.pro.scheduler.proto.stubs.scheduler_pb2_grpc as pb2_grpc
import tracardi.process_engine.action.v1.pro.scheduler.proto.stubs.scheduler_pb2 as pb2
from datetime import datetime, timedelta
from tracardi.service.pro.auth import get_tpro_token
from google.protobuf.json_format import ParseDict
from google.protobuf.struct_pb2 import Struct

with open(os.path.join(_local_dir, '../certs/server.crt'), 'rb') as f:
    trusted_certs = f.read()
credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)


class SchedulerClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, host, secure=False):
        self.host = host
        self.server_port = 50001

        # instantiate a channel
        host = '{}:{}'.format(self.host, self.server_port)
        if secure:
            self.channel = grpc.secure_channel(host, credentials)
        else:
            self.channel = grpc.insecure_channel(host)

        # bind the client and the server
        self.stub = pb2_grpc.ServiceStub(self.channel)

    @staticmethod
    def _to_struct(value: dict):
        return ParseDict(value, Struct(), )

    async def schedule(self, schedule_at, callback_host, source_id, profile_id, session_id, event_type, properties,
                       context, request):

        message = pb2.Payload(
            time=schedule_at,
            callback_host=callback_host,
            source_id=source_id,
            profile_id=profile_id,
            session_id=session_id,
            event_type=event_type,
            properties=self._to_struct(properties),
            context=self._to_struct(context),
            request=self._to_struct(request)
        )

        return self.stub.schedule_job(message, metadata=[('token', await get_tpro_token())])


if __name__ == '__main__':
    client = SchedulerClient("192.168.1.128")
    schedule_at = str(datetime.utcnow() + timedelta(seconds=60))
    result = client.schedule(
        schedule_at=schedule_at,
        callback_host="http://192.168.1.103:8686",
        source_id="d7a51074-d05d-4fbb-901e-bd494aa1bfb0",
        profile_id='1234',
        session_id="1234",
        event_type="aws7",
        properties={"a": 1,
                    "b": str(datetime.utcnow())},
        context={"c": 3},
        request={"request": 1}
    )
    print(f'{result}')
