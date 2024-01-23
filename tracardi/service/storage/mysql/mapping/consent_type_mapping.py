from tracardi.context import get_context
from tracardi.domain.consent_type import ConsentType
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import ConsentTypeTable

def map_to_consent_type_table(consent_type: ConsentType) -> ConsentTypeTable:
    context = get_context()
    return ConsentTypeTable(
        id=consent_type.id,
        tenant=context.tenant,
        production=context.production,
        name=consent_type.name,
        description=consent_type.description or "",
        revokable=consent_type.revokable if consent_type.revokable is not None else False,
        default_value=consent_type.default_value,
        enabled=consent_type.enabled if consent_type.enabled is not None else True,
        tags=",".join(consent_type.tags),  # Convert list of tags to a comma-separated string
        required=consent_type.required if consent_type.required is not None else False,
        auto_revoke=consent_type.auto_revoke  # Assuming auto_revoke is a JSON serializable field
    )

def map_to_consent_type(consent_type_table: ConsentTypeTable) -> ConsentType:
    return ConsentType(
        id=consent_type_table.id,
        name=consent_type_table.name,
        description=consent_type_table.description or "",
        revokable=consent_type_table.revokable if consent_type_table.revokable is not None else False,
        default_value=consent_type_table.default_value,
        enabled=consent_type_table.enabled if consent_type_table.enabled is not None else True,
        tags=split_list(consent_type_table.tags),  # Convert comma-separated string back to list
        required=consent_type_table.required if consent_type_table.required is not None else False,
        auto_revoke=consent_type_table.auto_revoke,

        production=consent_type_table.production,
        running=consent_type_table.running
    )
