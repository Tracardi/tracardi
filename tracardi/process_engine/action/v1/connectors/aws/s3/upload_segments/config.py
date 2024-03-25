from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    aws_access_key_id: str
    aws_secret_access_key: str
    s3_bucket: str

    @field_validator("aws_access_key_id")
    @classmethod
    def key_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("AWS Access Key ID can not be empty.")
        return value

    @field_validator("aws_secret_access_key")
    @classmethod
    def secret_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("AWS Secret Access Key can not be empty.")
        return value

    @field_validator("s3_bucket")
    @classmethod
    def bucket_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("S3 Bucket can not be empty.")
        return value