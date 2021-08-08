import base64
import json
from typing import List
from typing import Optional

from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.collection_crud import CollectionCrud
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.crud import StorageCrud


class Credential(NamedEntity):
    description: Optional[str] = ''
    type: str
    group: List[str] = ["General"]
    enabled: bool = True
    data: dict


class CredentialRecord(NamedEntity):
    description: Optional[str] = ''
    type: str
    enabled: bool = True
    data: str
    group: List[str] = ["General"]

    @staticmethod
    def encode(credential: Credential) -> 'CredentialRecord':
        json_data = json.dumps(credential.data)
        b64_data = base64.b64encode(json_data.encode('utf-8'))

        return CredentialRecord(
            id=credential.id,
            name=credential.name,
            description=credential.description,
            type=credential.type,
            enabled=credential.enabled,
            group=credential.group,
            data=b64_data
        )

    def decode(self) -> Credential:
        decoded = base64.b64decode(self.data)
        data = json.loads(decoded)

        return Credential(
            id=self.id,
            name=self.name,
            description=self.description,
            type=self.type,
            enabled=self.enabled,
            group=self.group,
            data=data
        )

    # Persistence

    def storage(self) -> StorageCrud:
        return StorageCrud("credential", CredentialRecord, entity=self)


class CredentialRecords(list):

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("credential", self)

    @staticmethod
    def decode(records: StorageResult) -> List[Credential]:
        return [CredentialRecord.decode(CredentialRecord(**record)) for record in records]
