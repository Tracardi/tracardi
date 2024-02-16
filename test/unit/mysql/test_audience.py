from com_tracardi.domain.audience.audience import Audience, AudienceGroupBy, DependentEntity, AudienceAggregate
from tracardi.context import Context, ServerContext
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.ref_value import RefValue
from com_tracardi.storage.audience_mapping import map_to_audience_table, map_to_audience
from tracardi.service.storage.mysql.schema.table import AudienceTable
from tracardi.service.storage.mysql.utils.serilizer import from_model


def test_map_to_audience_table_mapping():
    group_by = AudienceGroupBy(
        entity=DependentEntity(type='event',
                               event_type=NamedEntity(id="product-added-to-basket", name="Product Added To Basket"),
                               where=""),
        group_by=[
            AudienceAggregate(
                aggr='sum',
                by_field=RefValue(value="ec.product.price", ref=True),
                save_as="sum_of_price")
        ],
        group_where=""
    )

    context = Context(production=True, tenant="test")
    with ServerContext(context):
        audience = Audience(
            id="123",
            name="Test Audience",
            description="This is a test audience",
            enabled=True,
            tags=["Tag1", "Tag2"],
            join=[group_by],
            running=True,
            production=True
        )

        expected_audience_table = AudienceTable(
            id="123",
            name="Test Audience",
            description="This is a test audience",
            enabled=True,
            tags="Tag1,Tag2",
            join=from_model([group_by]),
            tenant="test",
            production=True,
            running=True
        )
        audience_table = map_to_audience_table(audience)

        assert audience_table.id == expected_audience_table.id
        assert audience_table.name == expected_audience_table.name
        assert audience_table.description == expected_audience_table.description
        assert audience_table.enabled == expected_audience_table.enabled
        assert audience_table.tags == expected_audience_table.tags
        assert audience_table.join == expected_audience_table.join

        audience1 = map_to_audience(audience_table)

        assert audience1 == audience