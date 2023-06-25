from typing import Dict
from tracardi.service.license import VALIDATOR, License, SCHEDULER
from tracardi.service.setup.domain.plugin_metadata import PluginMetadata, PluginTest

installed_plugins: Dict[str, PluginMetadata] = {

    "tracardi.process_engine.action.v1.internal.tag_event.plugin": PluginMetadata(
        test=PluginTest(init={"tags": "tag1,tag2"}, resource=None),
    ),

    "tracardi.process_engine.action.v1.time.last_profile_visit.plugin": PluginMetadata(
        test=PluginTest(init=None, resource=None),
    ),

    # "tracardi.process_engine.action.v1.internal.limiter.plugin": PluginMetadata(
    #     test=PluginTest(init={
    #         "keys": [],
    #         "limit": 10,
    #         "ttl": 60
    #     },
    #         resource=None)
    # ),

    "tracardi.process_engine.action.v1.connectors.telegram.post.plugin": PluginMetadata(
        test=PluginTest(
            init={'resource': {'id': 'id', 'name': 'name'}, 'message': 'test'},
            resource={
                "bot_token": "bot_token",
                "chat_id": 100
            }),
        plugin_registry="tracardi.process_engine.action.v1.connectors.telegram.post.registry"
    ),

    "tracardi.process_engine.action.v1.connectors.google.analytics.plugin": PluginMetadata(
        test=PluginTest(
            init={'source': {'id': 'id', 'name': 'name'}, 'category': 'category', 'action': 'action', 'label': 'label',
                  'value': 'value'},
            resource={
                "google_analytics_id": "google_analytics_id"
            }),
        plugin_registry="tracardi.process_engine.action.v1.connectors.google.analytics.registry"
    ),

    "tracardi.process_engine.action.v1.connectors.google.analytics_v4.plugin": PluginMetadata(
        test=PluginTest(
            init={'source': {'id': 'id', 'name': 'name'}, 'name': 'event_name', 'params': "payload@id"},
            resource={
                "api_key": "api_key",
                "measurement_id": "measurement_id"
            }),
        plugin_registry="tracardi.process_engine.action.v1.connectors.google.analytics_v4.registry"
    ),

    "tracardi.process_engine.action.v1.connectors.whois.plugin": PluginMetadata(
        test=PluginTest(init={"domain": "some.com"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.contains_pattern.plugin": PluginMetadata(
        test=PluginTest(init={"field": "payload@field", "pattern": "all"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.memory.collect.plugin": PluginMetadata(
        test=PluginTest(init={'name': 'Test name', 'type': 'list'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.password_generator_action": PluginMetadata(
        test=PluginTest(
            init={'lowercase': 4, 'max_length': 13, 'min_length': 8, 'special_characters': 2, 'uppercase': 2},
            resource=None)
    ),

    "tracardi.process_engine.action.v1.weekdays_checker_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),
    "tracardi.process_engine.action.v1.flow.start.start_action": PluginMetadata(
        test=PluginTest(init={'debug': False, 'event_id': None, 'event_type': {'id': '', 'name': ''}, 'event_types': [],
                              'profile_less': False, 'properties': '{}', 'session_less': False},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.flow.start_segmentation.plugin": PluginMetadata(
        test=PluginTest(init={'profile_id': "id"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.flow.property_exists.plugin": PluginMetadata(
        test=PluginTest(init={'property': 'event@context.page.url'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.end_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.raise_error_action": PluginMetadata(
        test=PluginTest(init={'message': 'Flow stopped due to error.'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.inject_action": PluginMetadata(
        test=PluginTest(init={'destination': 'payload', 'value': '{}'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.increase_views_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.increase_visits_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.increment_action": PluginMetadata(
        test=PluginTest(init={'field': 'profile@stats.counters.test', 'increment': 1},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.decrement_action": PluginMetadata(
        test=PluginTest(init={'decrement': 1, 'field': 'profile@stats.counters.test'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.if_action": PluginMetadata(
        test=PluginTest(init={'condition': 'event@id=="1"'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.starts_with_action": PluginMetadata(
        test=PluginTest(init={'field': 'event@id', 'prefix': 'test'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.ends_with_action": PluginMetadata(
        test=PluginTest(init={'field': 'event@id', 'prefix': 'test'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.new_visit_action": PluginMetadata(
        test=PluginTest(init={}, resource=None)
    ),

    "tracardi.process_engine.action.v1.new_profile_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.template_action": PluginMetadata(
        test=PluginTest(init={'template': ''},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.sort_dictionary": PluginMetadata(
        test=PluginTest(init={"direction": "asc", "data": "data", "sort_by": "key"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.misc.uuid4.plugin": PluginMetadata(
        test=PluginTest(init={}, resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.copy_trait_action": PluginMetadata(
        test=PluginTest(init={'traits': {'set': {}}},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.append_trait_action": PluginMetadata(
        test=PluginTest(
            init={'append': {'target1': 'source1', 'target2': 'source2'}, 'remove': {'target': ['item1', 'item2']}},
            resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.cut_out_trait_action": PluginMetadata(
        test=PluginTest(init={'trait': 'event@...'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.delete_trait_action": PluginMetadata(
        test=PluginTest(init={'delete': ['event@id']},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.auto_merge_properties_to_profile_action": PluginMetadata(
        test=PluginTest(init={'sub_traits': '', 'traits_type': 'public'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.assign_condition_result.plugin": PluginMetadata(
        test=PluginTest(init={'conditions': {}},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.condition_set.plugin": PluginMetadata(
        test=PluginTest(init={'conditions': {}},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.hash_traits_action": PluginMetadata(
        test=PluginTest(init={'func': 'md5', 'traits': []},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.mask_traits_action": PluginMetadata(
        test=PluginTest(init={'traits': []},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.join_payloads.plugin": PluginMetadata(
        test=PluginTest(init={'default': True, 'reshape': '{}', 'type': 'dict'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.merge_profiles_action": PluginMetadata(
        test=PluginTest(init={'mergeBy': ['profile@pii.email']},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.update_profile_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.discard_profile_update_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.update_event_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.update_session_action": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.reduce_array.plugin": PluginMetadata(
        test=PluginTest(init={'array': 'payload@test'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.calculator_action": PluginMetadata(
        test=PluginTest(init={'calc_dsl': 'a = profile@id + 1'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.mapping_action": PluginMetadata(
        test=PluginTest(init={'case_sensitive': False, 'mapping': {'a': 'profile@id'}, 'value': 'x'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.return_random_element_action": PluginMetadata(
        test=PluginTest(init={'list_of_items': [1, 2, 3, 4, 5]},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.log_action": PluginMetadata(
        test=PluginTest(init={'message': '<log-message>', 'type': 'warning'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.scrapper.xpath.plugin": PluginMetadata(
        test=PluginTest(init={'content': "", 'xpath': ""},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.operations.threshold.plugin": PluginMetadata(
        test=PluginTest(init={'assign_to_profile': True, 'name': "test", 'ttl': 1800, 'value': "1"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.geo.fence.circular.plugin": PluginMetadata(
        test=PluginTest(init={
            "center_coordinate": {"lat": 0, "lng": 0},
            "test_coordinate": {"lat": 0, "lng": 0},
            "radius": 10
        },
            resource=None)
    ),

    "tracardi.process_engine.action.v1.geo.distance.plugin": PluginMetadata(
        test=PluginTest(init={
            "start_coordinate": {"lat": 0, "lng": 0},
            "end_coordinate": {"lat": 0, "lng": 0},
        },
            resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.reshape_payload_action": PluginMetadata(
        test=PluginTest(init={'default': True, 'value': '{}'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.detect_client_agent_action": PluginMetadata(
        test=PluginTest(init={'agent': 'session@context.browser.browser.userAgent'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.traits.field_type_action": PluginMetadata(
        test=PluginTest(init={'field': "profile@id"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.events.event_discarder.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.profiles.profile_discarder.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.sessions.session_discarder.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.string_operations.plugin": PluginMetadata(
        test=PluginTest(init={'string': 'test'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.regex_match.plugin": PluginMetadata(
        test=PluginTest(init={'group_prefix': 'Group', 'pattern': '<pattern>', 'text': '<text or path to text>'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.regex_validator.plugin": PluginMetadata(
        test=PluginTest(init={'data': "a", 'validation_regex': "/a/"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.string_validator.plugin": PluginMetadata(
        test=PluginTest(init={'data': 'test', 'validator': 'test'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.string_splitter.plugin": PluginMetadata(
        test=PluginTest(init={'delimiter': '.', 'string': "test.test"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.string_join.plugin": PluginMetadata(
        test=PluginTest(init={'delimiter': ',', 'string': "payload@test"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.url_parser.plugin": PluginMetadata(
        test=PluginTest(init={'url': 'session@context.page.url'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.regex_replace.plugin": PluginMetadata(
        test=PluginTest(init={'find_regex': "abc", 'replace_with': "123", 'string': "abc"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.strings.string_similarity.plugin": PluginMetadata(
        test=PluginTest(init={'first_string': "abc", 'second_string': "abc", 'algorithm': "levenshtein"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.time.sleep_action": PluginMetadata(
        test=PluginTest(init={'wait': 1},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.time.today_action": PluginMetadata(
        test=PluginTest(init={'timezone': 'session@context.time.tz'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.time.day_night.plugin": PluginMetadata(
        test=PluginTest(init={'latitude': 1.2, 'longitude': 2.1},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.time.local_time_span.plugin": PluginMetadata(
        test=PluginTest(init={'end': "10:10:10", 'start': "12:10:10", 'timezone': 'session@context.time.tz'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.time.profile_live_time.plugin": PluginMetadata(
        test=PluginTest(init={'end': "10:10:10", 'start': "12:10:10", 'timezone': 'session@context.time.tz'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.time.time_difference.plugin": PluginMetadata(
        test=PluginTest(init={'now': 'now', 'reference_date': "12:10:10"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.ux.consent.plugin": PluginMetadata(
        test=PluginTest(
            init={'agree_all_event_type': 'agree-all-event-type', 'enabled': True, 'endpoint': 'http://localhost:8686',
                  'event_type': 'user-consent-pref', 'expand_height': 400, 'position': 'bottom',
                  'uix_source': 'http://localhost:8686'},
            resource=None)
    ),

    "tracardi.process_engine.action.v1.connectors.html.fetch.plugin": PluginMetadata(
        test=PluginTest(
            init={'body': '', 'cookies': {}, 'headers': {}, 'method': 'get', 'ssl_check': True, 'timeout': 30,
                  'url': "http://localhost"},
            resource=None)
    ),

    "tracardi.process_engine.action.v1.connectors.api_call.plugin": PluginMetadata(
        test=PluginTest(init={'body': {'content': '{}', 'type': 'application/json'}, 'cookies': {}, 'endpoint': "/test",
                              'headers': {},
                              'method': 'post', 'source': {'id': '1', 'name': 'Some value'}, 'ssl_check': True,
                              'timeout': 30},
                        resource={
                            "url": "http://localhost"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.smtp_call.plugin": PluginMetadata(
        test=PluginTest(init={
            'mail': {
                'message': {'content': 'ss', 'type': 'text/html'},
                'reply_to': 'mail@mail.co',
                'send_from': 'mail@mail.co',
                'send_to': 'mail@mail.co',
                'title': 'title'
            },
            'resource': {'id': '', 'name': ''}},
            resource={
                "smtp": "a",
                "port": 1,
                "username": "u",
                "password": "p"
            })
    ),

    "tracardi.process_engine.action.v1.segmentation.force.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.segmentation.has.plugin": PluginMetadata(
        test=PluginTest(init={"segment": "abc"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.segmentation.conditional.plugin": PluginMetadata(
        test=PluginTest(init={'condition': 'profile@id exists', 'false_action': 'remove', 'false_segment': 'xxx',
                              'true_action': 'add',
                              'true_segment': 'zzz'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.segmentation.add.plugin": PluginMetadata(
        test=PluginTest(init={'segment': 'abc'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.segmentation.delete.plugin": PluginMetadata(
        test=PluginTest(init={'segment': 'abc'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.segmentation.move.plugin": PluginMetadata(
        test=PluginTest(init={'from_segment': 'abc', 'to_segment': "asd"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.interest.add.plugin": PluginMetadata(
        test=PluginTest(init={'interest': 'abc', 'value': '1.0'},
                        resource=None)
    ),
    "tracardi.process_engine.action.v1.interest.increase.plugin": PluginMetadata(
        test=PluginTest(init={'interest': 'abc', 'value': '1.0'},
                        resource=None)
    ),
    "tracardi.process_engine.action.v1.interest.decrease.plugin": PluginMetadata(
        test=PluginTest(init={'interest': 'abc', 'value': '1.0'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.converters.data_to_json.plugin": PluginMetadata(
        test=PluginTest(init={'to_json': "{}"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.converters.json_to_data.plugin": PluginMetadata(
        test=PluginTest(init={'to_data': "{}"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.connectors.discord.push.plugin": PluginMetadata(
        test=PluginTest(
            init={'resource': {'id': 'id', 'name': 'name'},
                  'message': 'message',
                  'timeout': 10,
                  'username': "test"
                  },
            resource={
                "url": "http://webhook_url"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.maxmind.geoip.plugin": PluginMetadata(
        test=PluginTest(init={'ip': 'event@request.ip', 'source': {'id': '1', 'name': 'Some value'}},
                        resource={
                            "accountId": 123,
                            "license": 'test'
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.weather.msn_weather.plugin": PluginMetadata(
        test=PluginTest(init={'city': "London", 'system': 'C'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.connectors.oauth2_token.plugin": PluginMetadata(
        test=PluginTest(init={'destination': "payload@dest", 'source': {'id': '1', 'name': 'Some value'}},
                        resource={
                            "url": "http://url",
                            "token": "abc"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.slack.send_message.plugin": PluginMetadata(
        test=PluginTest(init={'channel': "xxx", 'message': "xxx", 'source': {'id': '1', 'name': 'Some value'}},
                        resource={
                            "token": "abc"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.google.sheets.modify.plugin": PluginMetadata(
        test=PluginTest(
            init={'range': "A1:A2", 'read': False, 'sheet_name': "sheet", 'source': {'id': '1', 'name': 'Some value'},
                  'spreadsheet_id': "1", 'values': '[["Name", "John"]]', 'write': False},
            resource={
                "api_key": "api_key"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.twitter.tweet.plugin": PluginMetadata(
        test=PluginTest(init={'source': {'id': '1', 'name': '1'}, 'tweet': 'tweet'},
                        resource={
                            'api_key': '<api_key',
                            'api_secret': '<api_secret>',
                            'access_token': '<access_token>',
                            'access_token_secret': '<access_token_secret>'
                        })
    ),

    "tracardi.process_engine.action.v1.internal.assign_profile_id.plugin": PluginMetadata(
        test=PluginTest(init={'value': ''},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.event_source_fetcher.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.inject_event.plugin": PluginMetadata(
        test=PluginTest(init={'event_id': "abc"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.inject_profile_by_field.plugin": PluginMetadata(
        test=PluginTest(init={'field': "pii.email", 'value': 'test@test.com'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.add_empty_profile.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.get_prev_event.plugin": PluginMetadata(
        test=PluginTest(init={'event_type': {'id': '@current', 'name': '@current'}, 'offset': -1},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.get_prev_session.plugin": PluginMetadata(
        test=PluginTest(init={'offset': -1},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.query_string.plugin": PluginMetadata(
        test=PluginTest(init={'index': "None", 'query': '', 'time_range': "+1d"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.add_empty_session.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.internal.add_response.plugin": PluginMetadata(
        test=PluginTest(init={'body': '{}', 'default': True, 'key': 'key'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.metrics.key_counter.plugin": PluginMetadata(
        test=PluginTest(init={'key': "1", 'save_in': "2"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.microservice.plugin": PluginMetadata(
        test=PluginTest(init={},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.consents.add_consent_action.plugin": PluginMetadata(
        test=PluginTest(init={'consents': 'aa'},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.consents.require_consents_action.plugin": PluginMetadata(
        test=PluginTest(init={'consent_ids': [], 'require_all': False},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.flow.postpone_event.plugin": PluginMetadata(
        test=PluginTest(init={
            'event_type': 'type',
            'source': {
                'id': 'x',
                'name': 'x'
            },
            'event_properties': '{}',
            'delay': 60},
            resource=None)
    ),

    "tracardi.process_engine.action.v1.contains_string_action": PluginMetadata(
        test=PluginTest(init={
            "field": "payload@field",
            "substring": "contains"
        })
    ),

    "tracardi.process_engine.action.v1.converters.base64.encode.plugin": PluginMetadata(
        test=PluginTest(init={
            'source': '',
            'source_encoding': '',
        },
            resource=None)
    ),

    "tracardi.process_engine.action.v1.converters.base64.decode.plugin": PluginMetadata(
        test=PluginTest(init={
            'source': '',
            'target_encoding': '',
        },
            resource=None)
    ),

    "tracardi.process_engine.action.v1.sort_array_action": PluginMetadata(
        test=PluginTest(init={"data": "event@properties.list_of_something", "direction": "asc"},
                        resource=None)
    ),

    "tracardi.process_engine.action.v1.connectors.github.issues.list.plugin": PluginMetadata(
        test=PluginTest(init={
            'resource': {
                'id': '',
                'name': '',
            },
            'timeout': 10,
            'owner': 'tracardi',
            'repo': 'tracardi',
        },
            resource={
                'api_url': 'https://api.github.com',
                'personal_access_token': '<your-PAT-here>',
            })
    ),

    "tracardi.process_engine.action.v1.connectors.github.issues.get.plugin": PluginMetadata(
        test=PluginTest(init={
            'resource': {
                'id': '',
                'name': '',
            },
            'timeout': 10,
            'owner': 'tracardi',
            'repo': 'tracardi',
            'issue_id': '1',
        },
            resource={
                'api_url': 'https://api.github.com',
                'personal_access_token': '<your-PAT-here>',
            })
    ),

    "tracardi.process_engine.action.v1.connectors.elasticsearch.query_local.plugin": PluginMetadata(
        test=PluginTest(
            init={'index': 'index', 'query': '{"query":{"match_all":{}}}'},
            resource=None)
    ),
}

if License.has_service(VALIDATOR):
    installed_plugins["com_tracardi.action.v1.validator.plugin"] = PluginMetadata(
        test=PluginTest(init={'validation_schema': {}}, resource=None)
    )

if License.has_service(SCHEDULER):
    installed_plugins["com_tracardi.action.v1.wait.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "resource": {
                    "id": "",
                    "name": ""
                },
                "postpone": 60
            },
            resource={"callback_host": "http://localhost"})
    )

if License.has_license():
    installed_plugins["com_tracardi.action.v1.sms.twilio.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "resource": {
                    "name": "",
                    "id": ""
                },
                "from_number": "xxx",
                "to_number": "yyy",
                "message": "zzz"
            },
            resource={
                "auth_token": "<token>",
                "account_sid": "<sid>"
            })
    )
    installed_plugins["com_tracardi.action.v1.ai.weaviate.delete.plugin"] = PluginMetadata(
        test=PluginTest(init={
            "resource": {
                "resource": {
                    "name": "",
                    "id": ""
                },
                "schema_class": "xxx",
                "object_id": "xxx"
            }
        }, resource={
            "url": "http://localhost",
            "weaviate_api_key": "optional",
            "username": "optional",
            "password": "optional",
            "scope": "optional",
            "headers": {
                "x_cohere_api_key": "optional",
                "x_huggingface_api_key": "optional",
                "x_openai_api_key": "optional",
            }
        }),
    )
    installed_plugins["com_tracardi.action.v1.ai.weaviate.exists.plugin"] = PluginMetadata(
        test=PluginTest(init={
            "resource": {
                "resource": {
                    "name": "",
                    "id": ""
                },
                "schema_class": "xxx",
                "object_id": "xxx"
            }
        }, resource={
            "url": "http://localhost",
            "weaviate_api_key": "optional",
            "username": "optional",
            "password": "optional",
            "scope": "optional",
            "headers": {
                "x_cohere_api_key": "optional",
                "x_huggingface_api_key": "optional",
                "x_openai_api_key": "optional",
            }
        }),
    )
    installed_plugins["com_tracardi.action.v1.ai.weaviate.get.plugin"] = PluginMetadata(
        test=PluginTest(init={
            "resource": {
                "resource": {
                    "name": "",
                    "id": ""
                },
                "schema_class": "xxx",
                "object_id": "xxx"
            }
        }, resource={
            "url": "http://localhost",
            "weaviate_api_key": "optional",
            "username": "optional",
            "password": "optional",
            "scope": "optional",
            "headers": {
                "x_cohere_api_key": "optional",
                "x_huggingface_api_key": "optional",
                "x_openai_api_key": "optional",
            }
        }),
    )
    installed_plugins["com_tracardi.action.v1.ai.weaviate.save.plugin"] = PluginMetadata(
        test=PluginTest(init={
            "resource": {
                "resource": {
                    "name": "",
                    "id": ""
                },
                "schema_class": "xxx",
                "object": "[]",
                "operation": "insert",
                "object_id": ""
            }
        }, resource={
            "url": "http://localhost",
            "weaviate_api_key": "optional",
            "username": "optional",
            "password": "optional",
            "scope": "optional",
            "headers": {
                "x_cohere_api_key": "optional",
                "x_huggingface_api_key": "optional",
                "x_openai_api_key": "optional",
            }
        }),
    )
    installed_plugins["com_tracardi.action.v1.ux.open_replay.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "token": ""
            },
            resource=None)
    )
    installed_plugins["com_tracardi.action.v1.ux.youtube_player.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "youtube_id": "",
                "title": ""
            },
            resource=None)
    )
    installed_plugins["com_tracardi.action.v1.ux.demo_form.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "api_url": "http://localhost:8686",
                "lifetime": "45",
                "horizontal_position": "right",
                "vertical_position": "bottom",
                "event_type": "request-demo"
            },
            resource=None)
    )
    installed_plugins["com_tracardi.action.v1.ux.generic.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "uix_source": "http://localhost/index.js"
            },
            resource=None)
    )
    installed_plugins["com_tracardi.action.v1.ux.rating_popup.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "api_url": "http://localhost:8686",
                "title": None,
                "message": None,
                "lifetime": "6",
                "horizontal_position": "center",
                "vertical_position": "bottom",
                "event_type": "rate",
                "save_event": True,
                "dark_theme": False
            },
            resource=None)
    )
    installed_plugins["com_tracardi.action.v1.sequencer.query.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "query": "",
                "intermediate": True
            },
            resource=None)
    )
    installed_plugins["com_tracardi.action.v1.sequencer.matcher.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "sequence": [],
                "list_of_events": {"ref": True, "value": "payload@sequence"}
            },
            resource=None)
    )

    installed_plugins["com_tracardi.action.v1.ai.openai.chatgpt.plugin"] = PluginMetadata(
        test=PluginTest(init={
            "resource": {
                "name": "",
                "id": ""
            },
            "prompt": ""
        }, resource={"api_key": "test"}),
    )

    installed_plugins["com_tracardi.action.v1.limiter.plugin"] = PluginMetadata(
        test=PluginTest(
            init={
                "keys": [],
                "limit": 10,
                "ttl": 60
            },
            resource=None)
    )

    installed_plugins["com_tracardi.action.v1.events.event_counter.plugin"] = PluginMetadata(
        test=PluginTest(init={
            "event_type": {'id': '1', 'name': 'Some value'},
            "time_span": "-15m"
        },
            resource=None)
    )

    installed_plugins["com_tracardi.action.v1.events.event_aggregator.plugin"] = PluginMetadata(
        test=PluginTest(init={
            "field": {'id': '1', 'name': 'Some value'},
            "time_span": "-15m"
        },
            resource=None)
    )

    installed_plugins["com_tracardi.action.v1.load_report.plugin"] = PluginMetadata(
        test=PluginTest(
            init={'report_config': {'params': '{}', 'report': {'id': '1', 'name': '1'}}},
            resource={

            })
    )

    installed_plugins["com_tracardi.action.v1.entity.upsert.plugin"] = PluginMetadata(
        test=PluginTest(init={'id': "1", 'properties': '{}', 'reference_profile': True, 'traits': '{}', 'type': 'type'},
                        resource=None)
    )

    installed_plugins["com_tracardi.action.v1.entity.load.plugin"] = PluginMetadata(
        test=PluginTest(init={'id': "1", 'reference_profile': True, 'type': {'id': 'type', 'name': 'type'}},
                        resource=None)
    )

    installed_plugins["com_tracardi.action.v1.entity.delete.plugin"] = PluginMetadata(
        test=PluginTest(init={'id': '1', 'reference_profile': True, 'type': {'id': 'type', 'name': 'type'}},
                        resource=None)
    )

    installed_plugins["com_tracardi.action.v1.segmentation.memorize.plugin"] = PluginMetadata(
        test=PluginTest(init={'memory_key': 'abc'},
                        resource=None)
    )

    installed_plugins["com_tracardi.action.v1.segmentation.recall.plugin"] = PluginMetadata(
        test=PluginTest(init={'memory_key': 'abc'},
                        resource=None)
    )

# Plugins only for testing
test_plugins: Dict[str, PluginMetadata] = {

    # Microservice
    # "tracardi.process_engine.action.v1.ux.generic.plugin": PluginTestTemplate(
    #     init={'props': {}, 'uix_source': None},
    #     resource=None
    # ),
    #
    # "tracardi.process_engine.action.v1.ux.contact_popup.plugin": PluginTestTemplate(
    #     init={'api_url': 'http://localhost:8686', 'contact_type': 'email', 'content': None, 'dark_theme': False,
    #           'event_type': None, 'horizontal_pos': 'center', 'save_event': True,
    #           'uix_source': 'http://localhost:8686',
    #           'vertical_pos': 'bottom'},
    #     resource=None
    # ),
    #
    # "tracardi.process_engine.action.v1.ux.snackbar.plugin": PluginTestTemplate(
    #     init={'hide_after': 6000, 'message': '', 'position_x': 'center', 'position_y': 'bottom', 'type': 'success',
    #           'uix_mf_source': 'http://localhost:8686'},
    #     resource=None
    # ),
    #
    # "tracardi.process_engine.action.v1.ux.cta_message.plugin": PluginTestTemplate(
    #     init={'border_radius': 2, 'border_shadow': 1, 'cancel_button': '', 'cta_button': '', 'cta_link': '',
    #           'hide_after': 6000, 'max_width': 500, 'message': '', 'min_width': 300, 'position_x': 'right',
    #           'position_y': 'bottom', 'title': '', 'uix_mf_source': 'http://localhost:8686'},
    #     resource=None
    # ),
    #
    # "tracardi.process_engine.action.v1.ux.rating_popup.plugin": PluginTestTemplate(
    #     init={'api_url': 'http://localhost:8686', 'dark_theme': False, 'event_type': None,
    #           'horizontal_position': 'center', 'lifetime': '6', 'message': None, 'save_event': True, 'title': None,
    #           'uix_source': 'http://localhost:8686', 'vertical_position': 'bottom'},
    #     resource=None
    # ),
    #
    # "tracardi.process_engine.action.v1.ux.question_popup.plugin": PluginTestTemplate(
    #     init={'api_url': 'http://localhost:8686', 'content': None, 'dark_theme': False, 'event_type': None,
    #           'horizontal_pos': 'center', 'left_button_text': None, 'popup_lifetime': '6', 'popup_title': None,
    #           'right_button_text': None, 'save_event': True, 'uix_source': 'http://localhost:8686',
    #           'vertical_pos': 'bottom'},
    #     resource=None
    # ),

    "tracardi.process_engine.action.v1.connectors.elasticsearch.query.plugin": PluginMetadata(
        test=PluginTest(init={'index': {'id': '1', 'name': 'Some value'}, 'query': '{"query":{"match_all":{}}}',
                              'source': {'id': '1', 'name': 'Some value'}},
                        resource={
                            "url": "host",
                            "port": 9200,
                            'scheme': 'https',
                            'verify_certs': False
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.sms77.sendsms.plugin": PluginMetadata(
        test=PluginTest(
            init={
                "resource": {
                    "id": "1",
                    "name": "1"
                },
                "message": "text",
                "recipient": "a",
                "sender": "b"
            },
            resource={
                "api_key": "api_key"
            }),
        plugin_registry="tracardi.process_engine.action.v1.connectors.sms77.sendsms.registry"
    ),

    "tracardi.process_engine.action.v1.connectors.influxdb.send.plugin": PluginMetadata(
        test=PluginTest(
            init={'bucket': "bucket", 'fields': {}, 'measurement': "measurement", 'organization': "measurement",
                  'source': {'id': '1', 'name': 'Some value'}, 'tags': {}, 'time': None},
            resource={
                "url": "http://localhost:8086",
                "token": "<token>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.influxdb.fetch.plugin": PluginMetadata(
        test=PluginTest(init={'aggregation': 'abc', 'bucket': "test", 'filters': {}, 'organization': 'test',
                              'source': {'id': '1', 'name': 'Some value'}, 'start': '-15m', 'stop': '0m'},
                        resource={
                            "url": "http://localhost:8086",
                            "token": "<token>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.add_contact.plugin": PluginMetadata(
        test=PluginTest(init={'additional_mapping': {}, 'email': "abc@test.com", 'source': {'id': "1", 'name': "1"}},
                        resource={
                            "api_key": "<api-key>",
                            "public_account_id": "<public-account-id>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.contact_status_change.plugin": PluginMetadata(
        test=PluginTest(init={'email': "test@rest.co", 'status': "status", 'source': {'id': "1", 'name': "1"}},
                        resource={
                            "api_key": "<api-key>",
                            "public_account_id": "<public-account-id>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.transactional_email.plugin": PluginMetadata(
        test=PluginTest(init={'message': {'content': {'content': '', "type": "text/plain"}, 'recipient': 'test@rest.co',
                                          'subject': 'subject'},
                              'sender_email': 'test@rest.co',
                              'source': {'id': '1', 'name': '1'}},
                        resource={
                            "api_key": "<api-key>",
                            "public_account_id": "<public-account-id>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.elastic_email.bulk_email.plugin": PluginMetadata(
        test=PluginTest(init={'message': {'content': {'content': '', "type": "text/plain"}, 'recipient': 'test@rest.co',
                                          'subject': 'subject'},
                              'sender_email': 'test@rest.co',
                              'source': {'id': '1', 'name': '1'}},
                        resource={
                            "api_key": "<api-key>",
                            "public_account_id": "<public-account-id>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.sendgrid.add_contact_to_list.plugin": PluginMetadata(
        test=PluginTest(init={'additional_mapping': {}, 'list_ids': "a,b", 'email': 'test@rest.co',
                              'source': {'id': '1', 'name': '1'}},
                        resource={
                            "token": "<token>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.sendgrid.add_email_to_global_suppression.plugin": PluginMetadata(
        test=PluginTest(init={'email': 'test@rest.co', 'source': {'id': '1', 'name': '1'}},
                        resource={
                            "token": "<token>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.sendgrid.send_email.plugin": PluginMetadata(
        test=PluginTest(init={'message': {'content': {'content': '', "type": "text/plain"}, 'recipient': 'test@rest.co',
                                          'subject': 'subject'},
                              'sender_email': 'test@rest.co',
                              'source': {'id': '1', 'name': '1'}},
                        resource={
                            "token": "<token>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.postgresql.query.plugin": PluginMetadata(
        test=PluginTest(init={'query': "select 1", 'source': {'id': '1', 'name': 'Some value'}, 'timeout': 20},
                        resource={
                            "host": '',
                            'database': 'database',
                            'user': 'user',
                            'password': 'password'
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.mongo.query.plugin": PluginMetadata(
        test=PluginTest(
            init={'collection': {'id': "1", "name": "1"}, 'database': {'id': "1", "name": "1"}, 'query': '{}',
                  'source': {'id': "1", "name": "1"}},
            resource={
                "uri": "mongodb://127.0.0.1:27017/",
                "timeout": 5000
            })
    ),

    "tracardi.process_engine.action.v1.connectors.mysql.query.plugin": PluginMetadata(
        test=PluginTest(
            init={'data': [], 'query': 'SELECT 1', 'source': {'id': '', 'name': ''}, 'timeout': 10, 'type': 'select'},
            resource={
                "host": "localhost",
                "port": 3306,
                "user": "<username>",
                "password": "",
                "database": "<database>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.salesforce.marketing_cloud.send.plugin": PluginMetadata(
        test=PluginTest(init={'extension_id': "1", 'mapping': {}, 'source': {'id': '', 'name': ''}, 'update': False},
                        resource={
                            "client_id": "<your-client-id>",
                            "client_secret": "<your-client-secret>",
                            "subdomain": "<your-subdomain>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.zapier.webhook.plugin": PluginMetadata(
        test=PluginTest(init={
            "url": "http://test.com",
            "body": "{}",
            "timeout": 30
        },
            resource=None)
    ),

    "tracardi.process_engine.action.v1.connectors.mqtt.publish.plugin": PluginMetadata(
        test=PluginTest(
            init={'payload': '{}', 'qos': '0', 'retain': False, 'source': {'id': '', 'name': ''}, 'topic': ''},
            resource={
                "url": "<url>",
                "port": 100,
                "username": "<username>",
                "password": "<password>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.mixpanel.send.plugin": PluginMetadata(
        test=PluginTest(init={'mapping': {}, 'source': {'id': '1', 'name': 'Some value'}},
                        resource={
                            "token": "token",
                            "server_prefix": "EU"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.mixpanel.fetch_funnel.plugin": PluginMetadata(
        test=PluginTest(init={'from_date': '2000-01-01', 'funnel_id': 1, 'project_id': 1,
                              'source': {'id': '1', 'name': 'Some value'},
                              'to_date': '2000-01-01'},
                        resource={
                            "token": "token",
                            "server_prefix": "EU",
                            'username': 'username',
                            'password': 'password'
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.airtable.send_record.plugin": PluginMetadata(
        test=PluginTest(
            init={'base_id': 1, 'mapping': {}, 'source': {'id': '1', 'name': 'Some value'}, 'table_name': "None"},
            resource={
                "api_key": "<your-api-key>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.airtable.fetch_records.plugin": PluginMetadata(
        test=PluginTest(
            init={'base_id': 1, 'formula': "None", 'source': {'id': '1', 'name': 'Some value'}, 'table_name': "None"},
            resource={
                "api_key": "<your-api-key>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.matomo.send_event.plugin": PluginMetadata(
        test=PluginTest(init={'dimensions': {}, 'goal_id': "None", 'rck': 'session@context.utm.term',
                              'rcn': 'session@context.utm.campaign', 'revenue': None, 'search_category': None,
                              'search_keyword': None,
                              'search_results_count': None, 'site_id': 1, 'source': {'id': '1', 'name': 'Some value'},
                              'url_ref': 'event@context.page.referer.host'},
                        resource={
                            "token": "<your-token>",
                            "api_url": "<your-matomo-url>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.hubspot.add_company.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "1",
                "name": "1"
            },
            "properties": {},
        },
            resource={
                "token": "<your-app-access-token>",
            })
    ),

    "tracardi.process_engine.action.v1.connectors.hubspot.add_contact.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "",
                "name": ""
            },
            "properties": [],
        },
            resource={
                "token": "<your-app-access-token>",
            })
    ),

    "tracardi.process_engine.action.v1.connectors.hubspot.get_company.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "",
                "name": ""
            },
            "company_id": "1",
        },
            resource={
                "token": "<your-app-access-token>",
            })
    ),

    "tracardi.process_engine.action.v1.connectors.hubspot.get_contact.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "",
                "name": ""
            },
            "contact_id": "1",
        },
            resource={
                "token": "<your-app-access-token>",
            })
    ),
    "tracardi.process_engine.action.v1.connectors.hubspot.update_company.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "",
                "name": ""
            },
            "company_id": "1",
            "properties": {}
        },
            resource={
                "token": "<your-app-access-token>",
            })
    ),
    "tracardi.process_engine.action.v1.connectors.hubspot.update_contact.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "",
                "name": ""
            },
            "contact_id": "1",
            'properties': {}
        },
            resource={
                "token": "<your-app-access-token>",
            })
    ),

    "tracardi.process_engine.action.v1.connectors.full_contact.person_enrich.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {"id": "1", "name": "2"},
            "pii": {}
        },
            resource={
                "token": "token"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.active_campaign.fetch_by_email.plugin": PluginMetadata(
        test=PluginTest(init={'email': "some@email.com", 'source': {'id': "", 'name': ""}},
                        resource={
                            "api_key": "<api-key>",
                            "api_url": "<api-url>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.active_campaign.add_contact.plugin": PluginMetadata(
        test=PluginTest(init={'fields': {}, 'source': {'id': "1", 'name': "1"}},
                        resource={
                            "api_key": "<api-key>",
                            "api_url": "<api-url>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.rabbitmq.publish.plugin": PluginMetadata(
        test=PluginTest(
            init={'queue': {'auto_declare': True, 'compression': None, 'name': "queue", 'queue_type': 'direct',
                            'routing_key': "None", 'serializer': 'json'}, 'source': {'id': "", "name": ""}},
            resource={
                "uri": "amqp://localhost:5672/",
                "port": "5672",
                "timeout": "5",
                "virtual_host": "",
            })
    ),

    "tracardi.process_engine.action.v1.connectors.civi_crm.add_contact.plugin": PluginMetadata(
        test=PluginTest(init={'contact_type': 'Individual', 'fields': {}, 'source': {'id': '', 'name': ''}},
                        resource={
                            "api_key": "<api-key>",
                            "site_key": "<site-key>",
                            "api_url": "http://localhost"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.amplitude.send_events.plugin": PluginMetadata(
        test=PluginTest(init={"source": {"id": "1", "name": '1'}},
                        resource={
                            "token": "token",

                        })
    ),

    "tracardi.process_engine.action.v1.connectors.aws.sqs.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {"id": '1', "name": '2'},
            "message": {'content': 'sssssss', 'type': 'plain/text'},
            "region_name": "",
            "queue_url": "http://test",
            "message_attributes": ""
        },
            resource={
                "aws_access_key_id": "str",
                "aws_secret_access_key": "str"
            })
    ),

    "tracardi.process_engine.action.v1.pro.scheduler.plugin": PluginMetadata(
        test=PluginTest(
            init={
                'resource': {"id": '1', "name": '2'},
                'source': {"id": '1', "name": '2'},
                'event_type': 'type',
                'postpone': 10
            },
            resource={
                "callback_host": "http://localhost:8686"
            }),
        plugin_registry="tracardi.process_engine.action.v1.pro.scheduler.registry"
    ),
    "tracardi.process_engine.action.v1.connectors.novu.trigger.plugin": PluginMetadata(
        test=PluginTest(
            init={'payload': '{}', 'recipient_email': 'profile@pii.email', 'source': {'id': '', 'name': ''},
                  'subscriber_id': 'profile@id', 'template': {'id': '', 'name': ''}},
            resource={
                "token": "token"
            }),
        plugin_registry="tracardi.process_engine.action.v1.connectors.novu.trigger.registry"
    ),

    "tracardi.process_engine.action.v1.connectors.pushover.push.plugin": PluginMetadata(
        test=PluginTest(init={
            'source': {'id': '', 'name': ''},
            'message': "test"
        },
            resource={
                "token": "<token>",
                "user": "<user>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.sentiment_analysis.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "",
                "name": ""
            },
            "language": "en",
            "text": "text"
        },
            resource={
                "token": "token"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.language_detection.plugin": PluginMetadata(
        test=PluginTest(init={
            'source': {
                'id': "",
                'name': ""
            },
            "message": "Hello world",
            "timeout": 15,
        },
            resource={
                "token": "token"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.text_classification.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "id": "",
                "name": ""
            },
            "language": "en",
            "model": "social",
            "title": "title",
            "text": "text"
        },
            resource={
                "token": "token"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.corporate_reputation.plugin": PluginMetadata(
        test=PluginTest(init={
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
            })
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.topics_extraction.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "name": "test",
                "id": "1"
            },
            "text": "test",
            "lang": "auto"
        },
            resource={
                "token": "token"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.summarization.plugin": PluginMetadata(
        test=PluginTest(init={
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
            })
    ),

    "tracardi.process_engine.action.v1.connectors.meaningcloud.deep_categorization.plugin": PluginMetadata(
        test=PluginTest(init={
            "source": {
                "name": "Test",
                "id": "1"
            },
            "text": "Text",
            "model": "IAB_2.0-tier3"
        },
            resource={
                "token": "token"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.add_contact.plugin": PluginMetadata(
        test=PluginTest(init={'additional_mapping': {}, 'email': "test@test.com", 'overwrite_with_blank': False,
                              'source': {'id': '1', 'name': 'Some value'}},
                        resource={
                            "public_key": "<client-public-key>",
                            "private_key": "<client-private-key>",
                            "api_url": "<url-of-mautic-instance>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_id.plugin": PluginMetadata(
        test=PluginTest(init={'contact_id': '1', 'source': {'id': "None", 'name': "None"}},
                        resource={
                            "public_key": "<client-public-key>",
                            "private_key": "<client-private-key>",
                            "api_url": "<url-of-mautic-instance>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_email.plugin": PluginMetadata(
        test=PluginTest(init={'contact_email': "test@test.com", 'source': {'id': "None", 'name': "None"}},
                        resource={
                            "public_key": "<client-public-key>",
                            "private_key": "<client-private-key>",
                            "api_url": "<url-of-mautic-instance>"
                        })
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.edit_points.plugin": PluginMetadata(
        test=PluginTest(
            init={'action': "add", 'contact_id': '1', 'points': 1, 'source': {'id': '1', 'name': 'Some value'}},
            resource={
                "public_key": "<client-public-key>",
                "private_key": "<client-private-key>",
                "api_url": "<url-of-mautic-instance>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.mautic.add_remove_segment.plugin": PluginMetadata(
        test=PluginTest(
            init={'action': "add", 'contact_id': '1', 'segment': "None", 'source': {'id': "None", 'name': "None"}},
            resource={
                "public_key": "<client-public-key>",
                "private_key": "<client-private-key>",
                "api_url": "<url-of-mautic-instance>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.mailchimp.transactional_email.plugin": PluginMetadata(
        test=PluginTest(
            init={'message': {'content': {'content': "None", 'type': 'text/html'}, 'recipient': "test@test.com",
                              'subject': "None"},
                  'sender_email': "test@test.com",
                  'source': {'id': '1', 'name': 'Some value'}},
            resource={
                "token": "<token>"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.mailchimp.add_to_audience.plugin": PluginMetadata(
        test=PluginTest(
            init={'email': "email@email.com", 'list_id': "1", 'merge_fields': {}, 'source': {'id': "1", 'name': "test"},
                  'subscribed': False, 'update': False},
            resource={
                "token": "1-2"
            })
    ),

    "tracardi.process_engine.action.v1.connectors.mailchimp.remove_from_audience.plugin": PluginMetadata(
        test=PluginTest(init={
            'delete': False,
            'email': 'test@test.com',
            'list_id': "None",
            'source': {
                'id': "None",
                'name': "None"
            }
        },
            resource={
                "token": "1-2"
            })
    ),

    "tracardi.process_engine.action.v1.operations.write_to_memory.plugin": PluginMetadata(
        test=PluginTest(init={'key': 'test-key', 'ttl': 15, 'value': 'test-value'},
                        resource={
                            "url": "<url>",
                            "user": "<user>",
                            "password": "<password>"
                        }),
    ),

    "tracardi.process_engine.action.v1.operations.read_from_memory.plugin": PluginMetadata(
        test=PluginTest(init={'key': 'test-key'},
                        resource={
                            "url": "<url>",
                            "user": "<user>",
                            "password": "<password>"
                        })
    ),

    # Moved to microservice
    # "tracardi.process_engine.action.v1.connectors.trello.add_card_action.plugin": PluginTestTemplate(
    #     init={
    #         "source": {
    #             "name": "test",
    #             "id": "1"
    #         },
    #         "board_url": "http://localhost",
    #         "list_name": "test",
    #         "card": {
    #             "name": "name",
    #             "desc": None,
    #             "urlSource": None,
    #             "coordinates": None,
    #             "due": None
    #         }
    #
    #     },
    #     resource={
    #         "api_key": "api_key",
    #         "token": "token"
    #     }
    # ),
    #
    # "tracardi.process_engine.action.v1.connectors.trello.delete_card_action.plugin": PluginTestTemplate(
    #     init={
    #         "source": {
    #             "name": "test",
    #             "id": "1"
    #         },
    #         "board_url": "http://localhost",
    #         "list_name": "list",
    #         "card_name": "card"
    #     },
    #     resource={
    #         "api_key": "api_key",
    #         "token": "token"
    #     }
    # ),
    #
    # "tracardi.process_engine.action.v1.connectors.trello.move_card_action.plugin": PluginTestTemplate(
    #     init={
    #         "source": {
    #             "name": "test",
    #             "id": "1"
    #         },
    #         "board_url": "http://localhost",
    #         "list_name1": "list1",
    #         "list_name2": "list2",
    #         "card_name": "card"
    #     },
    #     resource={
    #         "api_key": "api_key",
    #         "token": "token"
    #     }
    # ),
    #
    # "tracardi.process_engine.action.v1.connectors.trello.add_member_action.plugin": PluginTestTemplate(
    #     init={
    #         "source": {
    #             "name": "test",
    #             "id": "1"
    #         },
    #         "board_url": "http://locahost",
    #         "card_name": "card",
    #         "list_name": "list_name",
    #         "member_id": "1"
    #     },
    #     resource={
    #         "api_key": "api_key",
    #         "token": "token"
    #     }
    # ),
}
