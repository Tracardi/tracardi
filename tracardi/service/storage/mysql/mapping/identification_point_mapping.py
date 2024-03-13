from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.schema.table import IdentificationPointTable
from tracardi.domain.identification_point import IdentificationPoint, IdentificationField
from tracardi.context import get_context
from tracardi.service.storage.mysql.utils.serilizer import from_model, to_model


def map_to_identification_point_table(identification_point: IdentificationPoint) -> IdentificationPointTable:
    context = get_context()
    return IdentificationPointTable(
        id=identification_point.id,
        name=identification_point.name,
        description=identification_point.description or "",
        source_id=identification_point.source.id,
        source_name=identification_point.source.name,
        event_type_id=identification_point.event_type.id,
        event_type_name=identification_point.event_type.name,
        fields=from_model(identification_point.fields),
        enabled=identification_point.enabled,
        settings=identification_point.settings,
        tenant=context.tenant,
        production=context.production
    )


def map_to_identification_point(identification_point_table: IdentificationPointTable) -> IdentificationPoint:
    return IdentificationPoint(
        id=identification_point_table.id,
        name=identification_point_table.name,
        description=identification_point_table.description,
        source=NamedEntity(id=identification_point_table.source_id, name=identification_point_table.source_name),
        event_type=NamedEntity(id=identification_point_table.event_type_id, name=identification_point_table.event_type_name),
        fields=to_model(identification_point_table.fields, IdentificationField),
        enabled=identification_point_table.enabled if identification_point_table.enabled is not None else False,
        settings=identification_point_table.settings,

        production=identification_point_table.production,
        running=identification_point_table.running
    )
