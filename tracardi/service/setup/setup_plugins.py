from typing import Dict

from tracardi.service.plugin.plugin_install import install_plugins
from tracardi.service.setup.domain.plugin_test_template import PluginTestTemplate

installed_plugins: Dict[str, PluginTestTemplate] = {

    "tracardi.process_engine.action.v1.memory.collect.plugin": PluginTestTemplate(
        init={'name': 'Test name', 'type': 'list'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.password_generator_action": PluginTestTemplate(
        init={'lowercase': 4, 'max_length': 13, 'min_length': 8, 'special_characters': 2, 'uppercase': 2},
        resource=None
    ),

    "tracardi.process_engine.action.v1.weekdays_checker_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.flow.start.start_action": PluginTestTemplate(
        init={'debug': False, 'event_id': None, 'event_type': {'id': '', 'name': ''}, 'event_types': [],
              'profile_less': False, 'properties': '{}', 'session_less': False},
        resource=None
    ),

    "tracardi.process_engine.action.v1.flow.property_exists.plugin": PluginTestTemplate(
        init={'property': 'event@context.page.url'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.end_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.raise_error_action": PluginTestTemplate(
        init={'message': 'Flow stopped due to error.'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.inject_action": PluginTestTemplate(
        init={'destination': 'payload', 'value': '{}'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.increase_views_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.increase_visits_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.increment_action": PluginTestTemplate(
        init={'field': 'profile@stats.counters.test', 'increment': 1},
        resource=None
    ),

    "tracardi.process_engine.action.v1.decrement_action": PluginTestTemplate(
        init={'decrement': 1, 'field': 'profile@stats.counters.test'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.if_action": PluginTestTemplate(
        init={'condition': 'event@id=="1"'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.starts_with_action": PluginTestTemplate(
        init={'field': 'event@id', 'prefix': 'test'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ends_with_action": PluginTestTemplate(
        init={'field': 'event@id', 'prefix': 'test'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.new_visit_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.new_profile_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.template_action": PluginTestTemplate(
        init={'template': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.misc.uuid4.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.copy_trait_action": PluginTestTemplate(
        init={'traits': {'set': {}}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.append_trait_action": PluginTestTemplate(
        init={'append': {'target1': 'source1', 'target2': 'source2'}, 'remove': {'target': ['item1', 'item2']}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.cut_out_trait_action": PluginTestTemplate(
        init={'trait': 'event@...'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.delete_trait_action": PluginTestTemplate(
        init={'delete': ['event@id']},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.auto_merge_properties_to_profile_action": PluginTestTemplate(
        init={'sub_traits': '', 'traits_type': 'public'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.assign_condition_result.plugin": PluginTestTemplate(
        init={'conditions': {}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.condition_set.plugin": PluginTestTemplate(
        init={'conditions': {}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.hash_traits_action": PluginTestTemplate(
        init={'func': 'md5', 'traits': []},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.mask_traits_action": PluginTestTemplate(
        init={'traits': []},
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.join_payloads.plugin": PluginTestTemplate(
        init={'default': True, 'reshape': '{}', 'type': 'dict'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.merge_profiles_action": PluginTestTemplate(
        init={'mergeBy': ['profile@pii.email']},
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.segment_profile_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.update_profile_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.update_event_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.update_session_action": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.reduce_array.plugin": PluginTestTemplate(
        init={'array': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.write_to_memory.plugin": PluginTestTemplate(
        init={'key': 'test-key', 'ttl': 15, 'value': 'test-value'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.read_from_memory.plugin": PluginTestTemplate(
        init={'key': 'test-key'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.calculator_action": PluginTestTemplate(
        init={'calc_dsl': 'a = profile@id + 1'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.mapping_action": PluginTestTemplate(
        init={'case_sensitive': False, 'mapping': {'a': 'profile@id'}, 'value': 'x'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.return_random_element_action": PluginTestTemplate(
        init={'list_of_items': [1, 2, 3, 4, 5]},
        resource=None
    ),

    "tracardi.process_engine.action.v1.log_action": PluginTestTemplate(
        init={'message': '<log-message>', 'type': 'warning'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.scrapper.xpath.plugin": PluginTestTemplate(
        init={'content': "", 'xpath': ""},
        resource=None
    ),

    "tracardi.process_engine.action.v1.operations.threshold.plugin": PluginTestTemplate(
        init={'assign_to_profile': True, 'name': "test", 'ttl': 1800, 'value': "1"},
        resource=None
    ),

    "tracardi.process_engine.action.v1.geo.fence.circular.plugin": PluginTestTemplate(
        init={
            "center_coordinate": {"lat": 0, "lng": 0},
            "test_coordinate": {"lat": 0, "lng": 0},
            "radius": 10
        },
        resource=None
    ),

    "tracardi.process_engine.action.v1.geo.distance.plugin": PluginTestTemplate(
        init={
            "start_coordinate": {"lat": 0, "lng": 0},
            "end_coordinate": {"lat": 0, "lng": 0},
        },
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.reshape_payload_action": PluginTestTemplate(
        init={'default': True, 'value': '{}'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.detect_client_agent_action": PluginTestTemplate(
        init={'agent': 'session@context.browser.browser.userAgent'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.traits.field_type_action": PluginTestTemplate(
        init={'field': "profile@id"},
        resource=None
    ),

    "tracardi.process_engine.action.v1.events.event_counter.plugin": PluginTestTemplate(
        init={
            "event_type": "page-view",
            "time_span": "-15m"
        },
        resource=None
    ),

    "tracardi.process_engine.action.v1.events.event_aggregator.plugin": PluginTestTemplate(
        init={
            "field": 'event@type',
            "time_span": "-15m"
        },
        resource=None
    ),

    "tracardi.process_engine.action.v1.events.event_discarder.plugin": PluginTestTemplate(
        init={},
        resource=None
    ),

    "tracardi.process_engine.action.v1.json_schema_validation_action": PluginTestTemplate(
        init={'validation_schema': {}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.strings.string_operations.plugin": PluginTestTemplate(
        init={'string': 'test'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.strings.regex_match.plugin": PluginTestTemplate(
        init={'group_prefix': 'Group', 'pattern': '<pattern>', 'text': '<text or path to text>'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.strings.regex_validator.plugin": PluginTestTemplate(
        init={'data': "a", 'validation_regex': "/a/"},
        resource=None
    ),

    "tracardi.process_engine.action.v1.strings.string_validator.plugin": PluginTestTemplate(
        init={'data': 'test', 'validator': 'test'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.strings.string_splitter.plugin": PluginTestTemplate(
        init={'delimiter': '.', 'string': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.strings.url_parser.plugin": PluginTestTemplate(
        init={'url': 'session@context.page.url'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.strings.regex_replace.plugin": PluginTestTemplate(
        init={'find_regex': None, 'replace_with': None, 'string': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.time.sleep_action": PluginTestTemplate(
        init={'wait': 1},
        resource=None
    ),

    "tracardi.process_engine.action.v1.time.today_action": PluginTestTemplate(
        init={'timezone': 'session@context.time.tz'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.time.day_night.plugin": PluginTestTemplate(
        init={'latitude': None, 'longitude': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.time.local_time_span.plugin": PluginTestTemplate(
        init={'end': None, 'start': None, 'timezone': 'session@context.time.tz'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.time.time_difference.plugin": PluginTestTemplate(
        init={'now': 'now', 'reference_date': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ux.snackbar.plugin": PluginTestTemplate(
        init={'hide_after': 6000, 'message': '', 'position_x': 'center', 'position_y': 'bottom', 'type': 'success',
              'uix_mf_source': 'http://localhost:8686'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ux.consent.plugin": PluginTestTemplate(
        init={'agree_all_event_type': 'agree-all-event-type', 'enabled': True, 'endpoint': 'http://localhost:8686',
              'event_type': 'user-consent-pref', 'expand_height': 400, 'position': 'bottom',
              'uix_source': 'http://localhost:8686'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ux.cta_message.plugin": PluginTestTemplate(
        init={'border_radius': 2, 'border_shadow': 1, 'cancel_button': '', 'cta_button': '', 'cta_link': '',
              'hide_after': 6000, 'max_width': 500, 'message': '', 'min_width': 300, 'position_x': 'right',
              'position_y': 'bottom', 'title': '', 'uix_mf_source': 'http://localhost:8686'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ux.rating_popup.plugin": PluginTestTemplate(
        init={'api_url': 'http://localhost:8686', 'dark_theme': False, 'event_type': None,
              'horizontal_position': 'center', 'lifetime': '6', 'message': None, 'save_event': True, 'title': None,
              'uix_source': 'http://localhost:8686', 'vertical_position': 'bottom'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ux.question_popup.plugin": PluginTestTemplate(
        init={'api_url': 'http://localhost:8686', 'content': None, 'dark_theme': False, 'event_type': None,
              'horizontal_pos': 'center', 'left_button_text': None, 'popup_lifetime': '6', 'popup_title': None,
              'right_button_text': None, 'save_event': True, 'uix_source': 'http://localhost:8686',
              'vertical_pos': 'bottom'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ux.contact_popup.plugin": PluginTestTemplate(
        init={'api_url': 'http://localhost:8686', 'contact_type': 'email', 'content': None, 'dark_theme': False,
              'event_type': None, 'horizontal_pos': 'center', 'save_event': True, 'uix_source': 'http://localhost:8686',
              'vertical_pos': 'bottom'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.ux.generic.plugin": PluginTestTemplate(
        init={'props': {}, 'uix_source': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.html.fetch.plugin": PluginTestTemplate(
        init={'body': '', 'cookies': {}, 'headers': {}, 'method': 'get', 'ssl_check': True, 'timeout': 30, 'url': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.api_call.plugin": PluginTestTemplate(
        init={'body': {'content': '{}', 'type': 'application/json'}, 'cookies': {}, 'endpoint': None, 'headers': {},
              'method': 'post', 'source': {'id': '1', 'name': 'Some value'}, 'ssl_check': True, 'timeout': 30},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.smtp_call.plugin": PluginTestTemplate(
        init={'message': {'message': '', 'reply_to': '', 'send_from': '', 'send_to': '', 'title': ''},
              'source': {'id': '', 'name': ''}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.segments.profile_segmentation.plugin": PluginTestTemplate(
        init={'condition': '', 'false_action': 'remove', 'false_segment': '', 'true_action': 'add', 'true_segment': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.converters.data_to_json.plugin": PluginTestTemplate(
        init={'to_json': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.converters.json_to_data.plugin": PluginTestTemplate(
        init={'to_data': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mailchimp.transactional_email.plugin": PluginTestTemplate(
        init={'message': {'content': None, 'recipient': None, 'subject': None}, 'sender_email': None,
              'source': {'id': '1', 'name': 'Some value'}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.elasticsearch.query.plugin": PluginTestTemplate(
        init={'index': None, 'query': '{"query":{"match_all":{}}}', 'source': {'id': '1', 'name': 'Some value'}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mailchimp.add_to_audience.plugin": PluginTestTemplate(
        init={'email': None, 'list_id': None, 'merge_fields': {}, 'source': {'id': None, 'name': None},
              'subscribed': False, 'update': False},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mailchimp.remove_from_audience.plugin": PluginTestTemplate(
        init={
            'delete': False,
            'email': None,
            'list_id': None,
            'source': {
                'id': None,
                'name': None
            }
        },
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.trello.add_card_action.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "test",
                "id": "1"
            },
            "board_url": "http://localhost",
            "list_name": "test",
            "card": {
                "name": "name",
                "desc": None,
                "urlSource": None,
                "coordinates": None,
                "due": None
            }

        },
        resource={
            "api_key": "api_key",
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.trello.delete_card_action.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "test",
                "id": "1"
            },
            "board_url": "http://localhost",
            "list_name": "list",
            "card_name": "card"
        },
        resource={
            "api_key": "api_key",
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.trello.move_card_action.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "test",
                "id": "1"
            },
            "board_url": "http://localhost",
            "list_name1": "list1",
            "list_name2": "list2",
            "card_name": "card"
        },
        resource={
            "api_key": "api_key",
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.trello.add_member_action.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "test",
                "id": "1"
            },
            "board_url": "http://locahost",
            "card_name": "card",
            "list_name": "list_name",
            "member_id": "1"
        },
        resource={
            "api_key": "api_key",
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.amplitude.send_events.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mongo.query.plugin": PluginTestTemplate(
        init={'collection': None, 'database': None, 'query': '{}', 'source': {'id': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.full_contact.person_enrich.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.zapier.webhook.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.pushover.push.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.discord.push.plugin": PluginTestTemplate(
        init={'message': '', 'timeout': 10, 'url': None, 'username': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mqtt.publish.plugin": PluginTestTemplate(
        init={'payload': '{}', 'qos': '0', 'retain': False, 'source': {'id': '', 'name': ''}, 'topic': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.maxmind.geoip.plugin": PluginTestTemplate(
        init={'ip': 'event@metadata.ip', 'source': {'id': '1', 'name': 'Some value'}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mysql.query.plugin": PluginTestTemplate(
        init={'data': [], 'query': 'SELECT 1', 'source': {'id': '', 'name': ''}, 'timeout': 10, 'type': 'select'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.postgresql.query.plugin": PluginTestTemplate(
        init={'query': None, 'source': {'id': '1', 'name': 'Some value'}, 'timeout': 20},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.weather.msn_weather.plugin": PluginTestTemplate(
        init={'city': None, 'system': 'C'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.aws.sqs.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.sentiment_analysis.plugin": PluginTestTemplate(
        init=None,
        resource={
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.language_detection.plugin": PluginTestTemplate(
        init=None,
        resource={
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.text_classification.plugin": PluginTestTemplate(
        init=None,
        resource={
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.oauth2_token.plugin": PluginTestTemplate(
        init={'destination': None, 'source': {'id': '1', 'name': 'Some value'}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.slack.send_message.plugin": PluginTestTemplate(
        init={'channel': None, 'message': None, 'source': {'id': '1', 'name': 'Some value'}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.google.sheets.modify.plugin": PluginTestTemplate(
        init={'range': None, 'read': False, 'sheet_name': None, 'source': {'id': '1', 'name': 'Some value'},
              'spreadsheet_id': None, 'values': '[["Name", "John"]]', 'write': False},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.deep_categorization.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "Test",
                "id": "1"
            },
            "text": "Text",
            "model": "IAB_2.0-tier3"
        },
        resource={
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.corporate_reputation.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "Test",
                "id": "1"
            },
            "text": "text",
            "lang": "auto",
            "focus": "focus",
            "company_type": "type",
            "relaxed_typography": False
        },
        resource={
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.topics_extraction.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "test",
                "id": "1"
            },
            "text": "test",
            "lang": "auto"
        },
        resource={
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.summarization.plugin": PluginTestTemplate(
        init={
            "source": {
                "name": "Test",
                "id": "1"
            },
            "text": "text",
            "lang": "auto",
            "sentences": "2"
        },
        resource={
            "token": "token"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.influxdb.send.plugin": PluginTestTemplate(
        init={'bucket': None, 'fields': {}, 'measurement': None, 'organization': None,
              'source': {'id': '1', 'name': 'Some value'}, 'tags': {}, 'time': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.influxdb.fetch.plugin": PluginTestTemplate(
        init={'aggregation': None, 'bucket': None, 'filters': {}, 'organization': None,
              'source': {'id': '1', 'name': 'Some value'}, 'start': '-15m', 'stop': '0m'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mixpanel.send.plugin": PluginTestTemplate(
        init={'mapping': {}, 'source': {'id': '1', 'name': 'Some value'}},
        resource={
            "token": "token",
            "server_prefix": "EU"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.mixpanel.fetch_funnel.plugin": PluginTestTemplate(
        init={'from_date': None, 'funnel_id': None, 'project_id': None, 'source': {'id': '1', 'name': 'Some value'},
              'to_date': None},
        resource={
            "token": "token",
            "server_prefix": "EU"
        }
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.add_contact.plugin": PluginTestTemplate(
        init={'additional_mapping': {}, 'email': None, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.contact_status_change.plugin": PluginTestTemplate(
        init={'email': None, 'status': None, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.transactional_email.plugin": PluginTestTemplate(
        init={'message': {'content': '', 'recipient': '', 'subject': ''}, 'sender_email': '',
              'source': {'id': '', 'name': ''}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.bulk_email.plugin": PluginTestTemplate(
        init={'message': {'content': '', 'recipient': '', 'subject': ''}, 'sender_email': '',
              'source': {'id': '', 'name': ''}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.sendgrid.add_email_to_global_suppression.plugin": PluginTestTemplate(
        init={'email': None, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.add_contact.plugin": PluginTestTemplate(
        init={'additional_mapping': {}, 'email': None, 'overwrite_with_blank': False,
              'source': {'id': '1', 'name': 'Some value'}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_id.plugin": PluginTestTemplate(
        init={'contact_id': None, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_email.plugin": PluginTestTemplate(
        init={'contact_email': None, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.edit_points.plugin": PluginTestTemplate(
        init={'action': None, 'contact_id': None, 'points': None, 'source': {'id': '1', 'name': 'Some value'}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.add_remove_segment.plugin": PluginTestTemplate(
        init={'action': None, 'contact_id': None, 'segment': None, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.airtable.send_record.plugin": PluginTestTemplate(
        init={'base_id': None, 'mapping': {}, 'source': {'id': '1', 'name': 'Some value'}, 'table_name': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.airtable.fetch_records.plugin": PluginTestTemplate(
        init={'base_id': None, 'formula': None, 'source': {'id': '1', 'name': 'Some value'}, 'table_name': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.matomo.send_event.plugin": PluginTestTemplate(
        init={'dimensions': {}, 'goal_id': None, 'rck': 'session@context.utm.term',
              'rcn': 'session@context.utm.campaign', 'revenue': None, 'search_category': None, 'search_keyword': None,
              'search_results_count': None, 'site_id': None, 'source': {'id': '1', 'name': 'Some value'},
              'url_ref': 'event@context.page.referer.host'},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.civi_crm.add_contact.plugin": PluginTestTemplate(
        init={'contact_type': 'Individual', 'fields': {}, 'source': {'id': '', 'name': ''}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.active_campaign.fetch_by_email.plugin": PluginTestTemplate(
        init={'email': None, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.active_campaign.add_contact.plugin": PluginTestTemplate(
        init={'fields': {}, 'source': {'id': None, 'name': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.salesforce.marketing_cloud.send.plugin": PluginTestTemplate(
        init={'extension_id': None, 'mapping': {}, 'source': {'id': '', 'name': ''}, 'update': False},
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.novu.plugin": PluginTestTemplate(
        init={'payload': '{}', 'recipient_email': 'profile@pii.email', 'source': {'id': '', 'name': ''},
              'subscriber_id': 'profile@id', 'template_name': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.assign_profile_id.plugin": PluginTestTemplate(
        init={'value': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.event_source_fetcher.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.inject_event.plugin": PluginTestTemplate(
        init={'event_id': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.inject_profile.plugin": PluginTestTemplate(
        init={'query': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.add_empty_profile.plugin": PluginTestTemplate(
        init={},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.get_prev_event.plugin": PluginTestTemplate(
        init={'event_type': {'id': '@current', 'name': '@current'}, 'offset': -1},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.get_prev_session.plugin": PluginTestTemplate(
        init={'offset': -1},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.query_string.plugin": PluginTestTemplate(
        init={'index': None, 'query': '', 'time_range': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.add_empty_session.plugin": PluginTestTemplate(
        init={},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.entity.upsert.plugin": PluginTestTemplate(
        init={'id': None, 'properties': '{}', 'reference_profile': True, 'traits': '{}', 'type': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.entity.load.plugin": PluginTestTemplate(
        init={'id': None, 'reference_profile': True, 'type': {'id': '', 'name': ''}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.entity.delete.plugin": PluginTestTemplate(
        init={'id': '', 'reference_profile': True, 'type': {'id': '', 'name': ''}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.get_report.plugin": PluginTestTemplate(
        init={'report_config': {'params': '{}', 'report': {'id': '', 'name': ''}}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.internal.add_response.plugin": PluginTestTemplate(
        init={'body': '{}', 'default': True, 'key': ''},
        resource=None
    ),

    "tracardi.process_engine.action.v1.metrics.key_counter.plugin": PluginTestTemplate(
        init={'key': None, 'save_in': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.microservice.plugin": PluginTestTemplate(
        init={},
        resource=None
    ),

    "tracardi.process_engine.action.v1.consents.add_consent_action.plugin": PluginTestTemplate(
        init={'consents': None},
        resource=None
    ),

    "tracardi.process_engine.action.v1.consents.require_consents_action.plugin": PluginTestTemplate(
        init={'consent_ids': [], 'require_all': False},
        resource=None
    ),

    "tracardi.process_engine.action.v1.pro.scheduler.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.connectors.rabbitmq.publish.plugin": PluginTestTemplate(
        init={'queue': {'auto_declare': True, 'compression': None, 'name': None, 'queue_type': 'direct',
                        'routing_key': None, 'serializer': 'json'}, 'source': {'id': None}},
        resource=None
    ),

    "tracardi.process_engine.action.v1.flow.postpone_event.plugin": PluginTestTemplate(
        init=None,
        resource=None
    ),

    "tracardi.process_engine.action.v1.contains_string_action": PluginTestTemplate(
        init={
            "field": "payload@field",
            "substring": "contains"
        }
    )

}


async def add_plugins():
    return await install_plugins(installed_plugins)
