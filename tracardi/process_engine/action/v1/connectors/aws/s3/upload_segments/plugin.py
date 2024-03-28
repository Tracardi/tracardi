import json
from aiobotocore.session import get_session
import tempfile
import os
from datetime import datetime
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent
from .config import Config


def validate(config: dict) -> Config:
    return Config(**config)


class S3SegmentsUploaderPlugin(ActionRunner):
    config: Config

    async def set_up(self, config):
        self.config = validate(config)

    async def run(self, payload: dict, in_edge=None):
        try:
            session = get_session()
            async with session.create_client('s3',
                                             aws_secret_access_key=self.config.aws_secret_access_key,
                                             aws_access_key_id=self.config.aws_access_key_id) as s3:
                temp_segments_filename = ""
                segments_filename = self._generate_filename("segments")
                segments_exists = await self._check_s3_keys_exist(s3, self.config.s3_bucket, segments_filename)

                if 'traits' not in payload or 'smi_uid' not in payload['traits']:
                    return Result(port="error", value={"error": f"Could not find payload.traits.smi_uid"})

                segments_data = {
                    "profiles": [{"smi_uid": payload['traits']['smi_uid'], "segments": payload['segments']}]
                }
                if segments_exists:
                    temp_segments_filename = await self._download_s3_file(s3, self.config.s3_bucket, segments_filename)
                    with open(temp_segments_filename, 'r') as segments_file:
                        existing_segments_data = json.load(segments_file)
                        existing_segments_data['profiles'].append(
                            {"smi_uid": payload['traits']['smi_uid'], "segments": payload['segments']}
                        )
                    segments_data = existing_segments_data
                await self._upload_file_to_s3(s3, self.config.s3_bucket, segments_filename, segments_data)

                return Result(port="success", value={"message": "JSON data uploaded to S3."})

        except Exception as err:
            return Result(port="error", value={"error": f"S3 upload error: {err}"})

        finally:
            if os.path.exists(temp_segments_filename):
                os.remove(temp_segments_filename)

    @staticmethod
    async def _check_s3_keys_exist(s3_client, bucket: str, keys_to_check: list | str) -> bool:
        response = await s3_client.list_objects_v2(Bucket=bucket)
        if 'Contents' in response:
            existing_keys = {item['Key'] for item in response['Contents']}
            return keys_to_check in existing_keys
        return False

    @staticmethod
    async def _upload_file_to_s3(s3_client, bucket: str, filename: str, json_data: dict) -> None:
        await s3_client.put_object(
            Bucket=bucket,
            Key=filename,
            Body=json.dumps(json_data)
        )

    @staticmethod
    async def _download_s3_file(s3_client, bucket: str, filename: str) -> str:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
            response = await s3_client.get_object(Bucket=bucket, Key=filename)
            async with response['Body'] as stream:
                obj = await stream.read()
                with open(temp_filename, 'wb') as file:
                    file.write(obj)
            return temp_filename

    @staticmethod
    def _generate_filename(prefix: str) -> str:
        return f"{datetime.now().strftime('%Y-%m-%d')}_{prefix}.json"


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=S3SegmentsUploaderPlugin.__name__,
            init={
                "aws_access_key_id": "",
                "aws_secret_access_key": "",
                "s3_bucket": ""
            },
            version='0.9.0',
            manual='s3_segment_upload',
            form=Form(groups=[
                FormGroup(
                    name="S3 Upload Configuration",
                    description="Configure AWS credentials and S3 details",
                    fields=[
                        FormField(
                            id="aws_access_key_id",
                            name="AWS Access Key ID",
                            description="AWS Access Key ID",
                            component=FormComponent(type="password", props={"label": "AWS Access Key ID"})
                        ),
                        FormField(
                            id="aws_secret_access_key",
                            name="AWS Secret Access Key",
                            description="AWS Secret Access Key",
                            component=FormComponent(type="password", props={"label": "AWS Secret Access Key"})
                        ),
                        FormField(
                            id="s3_bucket",
                            name="S3 Bucket",
                            description="S3 Bucket to upload JSON data",
                            component=FormComponent(type="text", props={"label": "S3 Bucket"})
                        ),
                    ]
                ),
            ]),
            inputs=["payload"],
            outputs=["success", "error"],
            license="MIT",
            author="Eqwile"
        ),
        metadata=MetaData(
            name="S3 Segments Uploader Plugin",
            desc='Uploads user profile segments to S3 as JSON.',
            group=["AWS"],
            purpose=['collection', 'segmentation'],
            icon="aws"
        )
    )