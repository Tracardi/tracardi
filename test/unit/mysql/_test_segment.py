# from tracardi.context import Context, ServerContext
# from tracardi.domain.segment import Segment
# from tracardi.service.storage.mysql.mapping.segment_mapping import map_to_segment_table, map_to_segment
# from tracardi.service.storage.mysql.schema.table import SegmentTable
#
#
# def test_map_to_segment_table_with_correct_attributes():
#     with ServerContext(Context(production=True)):
#         segment = Segment(
#             id="segment_id",
#             name="Segment Name",
#             description="Segment Description",
#             eventType=["event_type_1", "event_type_2"],
#             condition="segment_condition",
#             enabled=True
#         )
#
#         result = map_to_segment_table(segment)
#
#         assert result.id == segment.id
#         assert result.name == segment.name
#         assert result.description == segment.description
#         assert result.event_type == "event_type_1,event_type_2"
#         assert result.condition == segment.condition
#         assert result.enabled == segment.enabled
#         assert result.machine_name == "segment-name"
#         assert result.production is True
#
#
# def test_map_to_segment_successfully():
#     segment_table = SegmentTable(
#         id="123",
#         name="Test Segment",
#         description="This is a test segment",
#         event_type="event_type_1,event_type_2",
#         condition="test_condition",
#         machine_name="test_segment"
#     )
#
#     expected_segment = Segment(
#         id="123",
#         name="Test Segment",
#         description="This is a test segment",
#         eventType=["event_type_1", "event_type_2"],
#         condition="test_condition",
#         enabled=True,
#         machine_name="test_segment"
#     )
#
#     assert map_to_segment(segment_table) == expected_segment
