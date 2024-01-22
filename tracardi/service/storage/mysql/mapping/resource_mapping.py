from datetime import datetime

from tracardi.context import get_context
from tracardi.domain.resource import Resource, ResourceCredentials
from tracardi.service.secrets import encrypt
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import ResourceTable
from tracardi.service.secrets import decrypt
from tracardi.domain.destination import DestinationConfig

def map_to_resource_table(resource: Resource) -> ResourceTable:
    context = get_context()
    return ResourceTable(
        id=resource.id,
        tenant=context.tenant,
        production=context.production,
        type=resource.type,
        timestamp=resource.timestamp or datetime.utcnow(),
        name=resource.name,
        description=resource.description,
        credentials=encrypt(resource.credentials) if resource.credentials else None,
        enabled=resource.enabled,
        tags=",".join(resource.tags) if isinstance(resource.tags, list) else resource.tags,
        groups=",".join(resource.groups) if isinstance(resource.groups, list) else resource.groups,
        icon=resource.icon,
        destination=encrypt(resource.destination) if resource.destination else None
    )


def map_to_resource(resource_table: ResourceTable) -> Resource:
    credentials = decrypt(resource_table.credentials) if resource_table.credentials else {"production": {}, "test": {}}
    destination = DestinationConfig(**decrypt(resource_table.destination)) if resource_table.destination else None
    return Resource(
        id=resource_table.id,
        name=resource_table.name,
        timestamp=resource_table.timestamp,
        description=resource_table.description,
        type=resource_table.type,
        tags=split_list(resource_table.tags),
        destination=destination,
        groups=split_list(resource_table.groups),
        icon=resource_table.icon,
        enabled=resource_table.enabled,
        credentials=ResourceCredentials(**credentials),

        production=resource_table.production,
        running=resource_table.running
    )
