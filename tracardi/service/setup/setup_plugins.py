from tracardi.service.plugin.plugin_install import install_plugins

installed_plugins = {

    "tracardi.process_engine.action.v1.memory.collect.plugin": {
        'name': "Test name", 'type': 'list'
    },
    "tracardi.process_engine.action.v1.password_generator_action": {
        'lowercase': 4,
        'max_length': 13,
        'min_length': 8,
        'special_characters': 2,
        'uppercase': 2},
    "tracardi.process_engine.action.v1.weekdays_checker_action": None,
    "tracardi.process_engine.action.v1.flow.start.start_action": {
        'debug': False,
        'event_id': None,
        'event_type': {
            'id': '', 'name': ''
        },
        'event_types': [],
        'profile_less': False,
        'properties': '{}',
        'session_less': False},
    "tracardi.process_engine.action.v1.flow.property_exists.plugin": {
        'property': 'event@context.page.url'
    },
    "tracardi.process_engine.action.v1.end_action": None,
    "tracardi.process_engine.action.v1.raise_error_action": {
        'message': 'Flow stopped due to error.'
    },
    "tracardi.process_engine.action.v1.inject_action": {
        'destination': 'payload', 'value': '{}'
    },
    "tracardi.process_engine.action.v1.increase_views_action": None,
    "tracardi.process_engine.action.v1.increase_visits_action": None,
    "tracardi.process_engine.action.v1.increment_action": {
        'field': 'profile@stats.counters.test', 'increment': 1},
    "tracardi.process_engine.action.v1.decrement_action": {
        'decrement': 1, 'field': 'profile@stats.counters.test'
    },
    "tracardi.process_engine.action.v1.if_action": {
        'condition': 'event@id=="1"'
    },
    "tracardi.process_engine.action.v1.starts_with_action": {
        'field': 'event@id', 'prefix': 'test'
    },
    "tracardi.process_engine.action.v1.ends_with_action": {
        'field': 'event@id', 'prefix': 'test'
    },
    "tracardi.process_engine.action.v1.new_visit_action": None,
    "tracardi.process_engine.action.v1.new_profile_action": None,
    "tracardi.process_engine.action.v1.template_action": {
        'template': ''
    },
    "tracardi.process_engine.action.v1.misc.uuid4.plugin": None,
    "tracardi.process_engine.action.v1.traits.copy_trait_action": {
        'traits': {
            'set': {}}
    },
    "tracardi.process_engine.action.v1.traits.append_trait_action": {
        'append': {
            'target1': 'source1', 'target2': 'source2'
        },
        'remove': {
            'target': ['item1', 'item2']}
    },
    "tracardi.process_engine.action.v1.traits.cut_out_trait_action": {
        'trait': 'event@...'
    },
    "tracardi.process_engine.action.v1.traits.delete_trait_action": {
        'delete': ['event@id']
    },
    "tracardi.process_engine.action.v1.traits.auto_merge_properties_to_profile_action": {
        'sub_traits': '',
        'traits_type': 'public'
    },
    "tracardi.process_engine.action.v1.traits.assign_condition_result.plugin": {
        'conditions': {}
    },
    "tracardi.process_engine.action.v1.traits.condition_set.plugin": {
        'conditions': {}
    },
    "tracardi.process_engine.action.v1.traits.hash_traits_action": {
        'func': 'md5', 'traits': []
    },
    "tracardi.process_engine.action.v1.traits.mask_traits_action": {
        'traits': []
    },
    "tracardi.process_engine.action.v1.operations.join_payloads.plugin": {
        'default': True, 'reshape': '{}',
        'type': 'dict'
    },
    "tracardi.process_engine.action.v1.operations.merge_profiles_action": {
        'mergeBy': ['profile@pii.email']
    },
    "tracardi.process_engine.action.v1.operations.segment_profile_action": None,
    "tracardi.process_engine.action.v1.operations.update_profile_action": None,
    "tracardi.process_engine.action.v1.operations.update_event_action": None,
    "tracardi.process_engine.action.v1.operations.update_session_action": None,
    "tracardi.process_engine.action.v1.operations.reduce_array.plugin": {
        'array': ""
    },
    "tracardi.process_engine.action.v1.operations.write_to_memory.plugin": {
        'key': "test-key", 'ttl': 15,
        'value': "test-value"
    },
    "tracardi.process_engine.action.v1.operations.read_from_memory.plugin": {
        'key': "test-key"
    },
    "tracardi.process_engine.action.v1.calculator_action": {
        'calc_dsl': 'a = profile@id + 1'
    },
    "tracardi.process_engine.action.v1.mapping_action": {
        'case_sensitive': False,
        'mapping': {"a": "profile@id"
                    },
        'value': "x"
    },
    "tracardi.process_engine.action.v1.return_random_element_action": {
        'list_of_items': [1, 2, 3, 4, 5]
    },
    "tracardi.process_engine.action.v1.log_action": {
        'message': '<log-message>', 'type': 'warning'
    },
    "tracardi.process_engine.action.v1.scrapper.xpath.plugin": {
        'content': None, 'xpath': None},
    "tracardi.process_engine.action.v1.operations.threshold.plugin": {
        'assign_to_profile': True, 'name': None,
        'ttl': 1800, 'value': None},
    "tracardi.process_engine.action.v1.geo.fence.circular.plugin": None,
    "tracardi.process_engine.action.v1.geo.distance.plugin": None,
    "tracardi.process_engine.action.v1.traits.reshape_payload_action": {
        'default': True, 'value': '{}'
    },
    "tracardi.process_engine.action.v1.detect_client_agent_action": {
        'agent': 'session@context.browser.browser.userAgent'
    },
    "tracardi.process_engine.action.v1.traits.field_type_action": {
        'field': None},
    "tracardi.process_engine.action.v1.events.event_counter.plugin": None,
    "tracardi.process_engine.action.v1.events.event_aggregator.plugin": None,
    "tracardi.process_engine.action.v1.events.event_discarder.plugin": None,
    "tracardi.process_engine.action.v1.json_schema_validation_action": {
        'validation_schema': {}
    },
    "tracardi.process_engine.action.v1.strings.string_operations.plugin": {
        'string': ''
    },
    "tracardi.process_engine.action.v1.strings.regex_match.plugin": {
        'group_prefix': 'Group',
        'pattern': '<pattern>',
        'text': '<text or path to text>'
    },
    "tracardi.process_engine.action.v1.strings.regex_validator.plugin": {
        'data': None, 'validation_regex': None},
    "tracardi.process_engine.action.v1.strings.string_validator.plugin": {
        'data': None, 'validator': None},
    "tracardi.process_engine.action.v1.strings.string_splitter.plugin": {
        'delimiter': '.', 'string': None},
    "tracardi.process_engine.action.v1.strings.url_parser.plugin": {
        'url': 'session@context.page.url'
    },
    "tracardi.process_engine.action.v1.strings.regex_replace.plugin": {
        'find_regex': None, 'replace_with': None,
        'string': None},
    "tracardi.process_engine.action.v1.time.sleep_action": {
        'wait': 1},
    "tracardi.process_engine.action.v1.time.today_action": {
        'timezone': 'session@context.time.tz'
    },
    "tracardi.process_engine.action.v1.time.day_night.plugin": {
        'latitude': None, 'longitude': None},
    "tracardi.process_engine.action.v1.time.local_time_span.plugin": {
        'end': None, 'start': None,
        'timezone': 'session@context.time.tz'
    },
    "tracardi.process_engine.action.v1.time.time_difference.plugin": {
        'now': 'now', 'reference_date': None},
    "tracardi.process_engine.action.v1.ux.snackbar.plugin": {
        'hide_after': 6000,
        'message': '',
        'position_x': 'center',
        'position_y': 'bottom',
        'type': 'success',
        'uix_mf_source': 'http://localhost:8686'
    },
    "tracardi.process_engine.action.v1.ux.consent.plugin": {
        'agree_all_event_type': 'agree-all-event-type',
        'enabled': True,
        'endpoint': 'http://localhost:8686',
        'event_type': 'user-consent-pref',
        'expand_height': 400,
        'position': 'bottom',
        'uix_source': 'http://localhost:8686'
    },
    "tracardi.process_engine.action.v1.ux.cta_message.plugin": {
        'border_radius': 2,
        'border_shadow': 1,
        'cancel_button': '',
        'cta_button': '',
        'cta_link': '',
        'hide_after': 6000,
        'max_width': 500,
        'message': '',
        'min_width': 300,
        'position_x': 'right',
        'position_y': 'bottom',
        'title': '',
        'uix_mf_source': 'http://localhost:8686'
    },
    "tracardi.process_engine.action.v1.ux.rating_popup.plugin": {
        'api_url': 'http://localhost:8686',
        'dark_theme': False,
        'event_type': None,
        'horizontal_position': 'center',
        'lifetime': '6',
        'message': None,
        'save_event': True,
        'title': None,
        'uix_source': 'http://localhost:8686',
        'vertical_position': 'bottom'
    },
    "tracardi.process_engine.action.v1.ux.question_popup.plugin": {
        'api_url': 'http://localhost:8686',
        'content': None,
        'dark_theme': False,
        'event_type': None,
        'horizontal_pos': 'center',
        'left_button_text': None,
        'popup_lifetime': '6',
        'popup_title': None,
        'right_button_text': None,
        'save_event': True,
        'uix_source': 'http://localhost:8686',
        'vertical_pos': 'bottom'
    },
    "tracardi.process_engine.action.v1.ux.contact_popup.plugin": {
        'api_url': 'http://localhost:8686',
        'contact_type': 'email',
        'content': None,
        'dark_theme': False,
        'event_type': None,
        'horizontal_pos': 'center',
        'save_event': True,
        'uix_source': 'http://localhost:8686',
        'vertical_pos': 'bottom'
    },
    "tracardi.process_engine.action.v1.ux.generic.plugin": {
        'props': {}, 'uix_source': None},
    "tracardi.process_engine.action.v1.connectors.html.fetch.plugin": {
        'body': '',
        'cookies': {},
        'headers': {},
        'method': 'get',
        'ssl_check': True,
        'timeout': 30,
        'url': None},
    "tracardi.process_engine.action.v1.connectors.api_call.plugin": {
        'body': {
            'content': '{}', 'type': 'application/json'
        },
        'cookies': {},
        'endpoint': None,
        'headers': {},
        'method': 'post',
        'source': {
            'id': "1", 'name': "Some value"},
        'ssl_check': True,
        'timeout': 30},
    "tracardi.process_engine.action.v1.connectors.smtp_call.plugin": {
        'message': {
            'message': '',
            'reply_to': '',
            'send_from': '',
            'send_to': '',
            'title': ''
        },
        'source': {
            'id': '', 'name': ''}
    },
    "tracardi.process_engine.action.v1.segments.profile_segmentation.plugin": {
        'condition': '',
        'false_action': 'remove',
        'false_segment': '',
        'true_action': 'add',
        'true_segment': ''
    },
    "tracardi.process_engine.action.v1.converters.data_to_json.plugin": {
        'to_json': None},
    "tracardi.process_engine.action.v1.converters.json_to_data.plugin": {
        'to_data': None},
    "tracardi.process_engine.action.v1.connectors.mailchimp.transactional_email.plugin": {
        'message': {
            'content': None, 'recipient': None, 'subject': None},
        'sender_email': None,
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.elasticsearch.query.plugin": {
        'index': None,
        'query': '{"query":{"match_all":{}}}',
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.mailchimp.add_to_audience.plugin": {
        'email': None,
        'list_id': None,
        'merge_fields': {},
        'source': {
            'id': None,
            'name': None},
        'subscribed': False,
        'update': False},
    "tracardi.process_engine.action.v1.connectors.mailchimp.remove_from_audience.plugin": {
        'delete': False,
        'email': None,
        'list_id': None,
        'source': {
            'id': None,
            'name': None}
    },
    "tracardi.process_engine.action.v1.connectors.trello.add_card_action.plugin": None,
    "tracardi.process_engine.action.v1.connectors.trello.delete_card_action.plugin": None,
    "tracardi.process_engine.action.v1.connectors.trello.move_card_action.plugin": None,
    "tracardi.process_engine.action.v1.connectors.trello.add_member_action.plugin": None,
    "tracardi.process_engine.action.v1.connectors.amplitude.send_events.plugin": None,
    "tracardi.process_engine.action.v1.connectors.mongo.query.plugin": {
        'collection': None, 'database': None,
        'query': '{}', 'source': {
            'id': None}
    },
    "tracardi.process_engine.action.v1.connectors.full_contact.person_enrich.plugin": None,
    "tracardi.process_engine.action.v1.connectors.zapier.webhook.plugin": None,
    "tracardi.process_engine.action.v1.connectors.pushover.push.plugin": None,
    "tracardi.process_engine.action.v1.connectors.discord.push.plugin": {
        'message': '', 'timeout': 10, 'url': None,
        'username': None},
    "tracardi.process_engine.action.v1.connectors.mqtt.publish.plugin": {
        'payload': '{}',
        'qos': '0',
        'retain': False,
        'source': {
            'id': '', 'name': ''
        },
        'topic': ''
    },
    "tracardi.process_engine.action.v1.connectors.maxmind.geoip.plugin": {
        'ip': 'event@metadata.ip',
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.mysql.query.plugin": {
        'data': [],
        'query': 'SELECT 1',
        'source': {
            'id': '', 'name': ''
        },
        'timeout': 10,
        'type': 'select'
    },
    "tracardi.process_engine.action.v1.connectors.postgresql.query.plugin": {
        'query': None,
        'source': {
            'id': "1", 'name': "Some value"},
        'timeout': 20},
    "tracardi.process_engine.action.v1.connectors.weather.msn_weather.plugin": {
        'city': None, 'system': 'C'
    },
    "tracardi.process_engine.action.v1.connectors.aws.sqs.plugin": None,
    "tracardi.process_engine.action.v1.connectors.meaningcloud.sentiment_analysis.plugin": None,
    "tracardi.process_engine.action.v1.connectors.meaningcloud.language_detection.plugin": None,
    "tracardi.process_engine.action.v1.connectors.meaningcloud.text_classification.plugin": None,
    "tracardi.process_engine.action.v1.connectors.oauth2_token.plugin": {
        'destination': None,
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.slack.send_message.plugin": {
        'channel': None, 'message': None,
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.google.sheets.modify.plugin": {
        'range': None,
        'read': False,
        'sheet_name': None,
        'source': {
            'id': "1", 'name': "Some value"},
        'spreadsheet_id': None,
        'values': '[["Name", "John"]]',
        'write': False},
    "tracardi.process_engine.action.v1.connectors.meaningcloud.deep_categorization.plugin": None,
    "tracardi.process_engine.action.v1.connectors.meaningcloud.corporate_reputation.plugin": None,
    "tracardi.process_engine.action.v1.connectors.meaningcloud.topics_extraction.plugin": None,
    "tracardi.process_engine.action.v1.connectors.meaningcloud.summarization.plugin": None,
    "tracardi.process_engine.action.v1.connectors.influxdb.send.plugin": {
        'bucket': None,
        'fields': {},
        'measurement': None,
        'organization': None,
        'source': {
            'id': "1", 'name': "Some value"},
        'tags': {},
        'time': None},
    "tracardi.process_engine.action.v1.connectors.influxdb.fetch.plugin": {
        'aggregation': None,
        'bucket': None,
        'filters': {},
        'organization': None,
        'source': {
            'id': "1", 'name': "Some value"},
        'start': '-15m',
        'stop': '0m'
    },
    "tracardi.process_engine.action.v1.connectors.mixpanel.send.plugin": {
        'mapping': {},
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.mixpanel.fetch_funnel.plugin": {
        'from_date': None,
        'funnel_id': None,
        'project_id': None,
        'source': {
            'id': "1", 'name': "Some value"},
        'to_date': None},
    "tracardi.process_engine.action.v1.connectors.elastic_email.add_contact.plugin": {
        'additional_mapping': {},
        'email': None,
        'source': {
            'id': None,
            'name': None}
    },
    "tracardi.process_engine.action.v1.connectors.elastic_email.transactional_email.plugin": {
        'message': {
            'content': '', 'recipient': '', 'subject': ''
        },
        'sender_email': '',
        'source': {
            'id': '', 'name': ''}
    },
    "tracardi.process_engine.action.v1.connectors.elastic_email.bulk_email.plugin": {
        'message': {
            'content': '', 'recipient': '', 'subject': ''
        },
        'sender_email': '',
        'source': {
            'id': '', 'name': ''}
    },
    "tracardi.process_engine.action.v1.connectors.mautic.add_contact.plugin": {
        'additional_mapping': {},
        'email': None,
        'overwrite_with_blank': False,
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_id.plugin": {
        'contact_id': None,
        'source': {
            'id': None,
            'name': None}
    },
    "tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_email.plugin": {
        'contact_email': None,
        'source': {
            'id': None,
            'name': None}
    },
    "tracardi.process_engine.action.v1.connectors.mautic.edit_points.plugin": {
        'action': None,
        'contact_id': None,
        'points': None,
        'source': {
            'id': "1", 'name': "Some value"}
    },
    "tracardi.process_engine.action.v1.connectors.mautic.add_remove_segment.plugin": {
        'action': None,
        'contact_id': None,
        'segment': None,
        'source': {
            'id': None,
            'name': None}
    },
    "tracardi.process_engine.action.v1.connectors.airtable.send_record.plugin": {
        'base_id': None,
        'mapping': {},
        'source': {
            'id': "1", 'name': "Some value"},
        'table_name': None},
    "tracardi.process_engine.action.v1.connectors.airtable.fetch_records.plugin": {
        'base_id': None,
        'formula': None,
        'source': {
            'id': "1", 'name': "Some value"},
        'table_name': None},
    "tracardi.process_engine.action.v1.connectors.matomo.send_event.plugin": {
        'dimensions': {},
        'goal_id': None,
        'rck': 'session@context.utm.term',
        'rcn': 'session@context.utm.campaign',
        'revenue': None,
        'search_category': None,
        'search_keyword': None,
        'search_results_count': None,
        'site_id': None,
        'source': {
            'id': "1", 'name': "Some value"},
        'url_ref': 'event@context.page.referer.host'
    },
    "tracardi.process_engine.action.v1.connectors.civi_crm.add_contact.plugin": {
        'contact_type': 'Individual',
        'fields': {},
        'source': {
            'id': '', 'name': ''}
    },
    "tracardi.process_engine.action.v1.connectors.active_campaign.fetch_by_email.plugin": {
        'email': None,
        'source': {
            'id': None,
            'name': None}
    },
    "tracardi.process_engine.action.v1.connectors.active_campaign.add_contact.plugin": {
        'fields': {},
        'source': {
            'id': None,
            'name': None}
    },
    "tracardi.process_engine.action.v1.connectors.salesforce.marketing_cloud.send.plugin": {
        'extension_id': None,
        'mapping': {},
        'source': {
            'id': '',
            'name': ''
        },
        'update': False},
    "tracardi.process_engine.action.v1.connectors.novu.plugin": {
        'payload': '{}',
        'recipient_email': 'profile@pii.email',
        'source': {
            'id': '', 'name': ''
        },
        'subscriber_id': 'profile@id',
        'template_name': None},
    "tracardi.process_engine.action.v1.internal.assign_profile_id.plugin": {
        'value': ''
    },
    "tracardi.process_engine.action.v1.internal.event_source_fetcher.plugin": None,
    "tracardi.process_engine.action.v1.internal.inject_event.plugin": {
        'event_id': None},
    "tracardi.process_engine.action.v1.internal.inject_profile.plugin": {
        'query': ''
    },
    "tracardi.process_engine.action.v1.internal.add_empty_profile.plugin": {},
    "tracardi.process_engine.action.v1.internal.get_prev_event.plugin": {
        'event_type': {
            'id': '@current', 'name': '@current'
        }, 'offset': -1},
    "tracardi.process_engine.action.v1.internal.get_prev_session.plugin": {
        'offset': -1},
    "tracardi.process_engine.action.v1.internal.query_string.plugin": {
        'index': None, 'query': '', 'time_range': None},
    "tracardi.process_engine.action.v1.internal.add_empty_session.plugin": {},
    "tracardi.process_engine.action.v1.internal.entity.upsert.plugin": {
        'id': None,
        'properties': '{}',
        'reference_profile': True,
        'traits': '{}',
        'type': ''
    },
    "tracardi.process_engine.action.v1.internal.entity.load.plugin": {
        'id': None, 'reference_profile': True,
        'type': {
            'id': '', 'name': ''}
    },
    "tracardi.process_engine.action.v1.internal.entity.delete.plugin": {
        'id': '', 'reference_profile': True,
        'type': {
            'id': '', 'name': ''}
    },
    "tracardi.process_engine.action.v1.internal.get_report.plugin": {
        'report_config': {
            'params': '{}', 'report': {
                'id': '', 'name': ''}}
    },
    "tracardi.process_engine.action.v1.internal.add_response.plugin": {
        'body': '{}', 'default': True, 'key': ''
    },
    "tracardi.process_engine.action.v1.metrics.key_counter.plugin": {
        'key': None, 'save_in': None},
    "tracardi.process_engine.action.v1.microservice.plugin": {},
    "tracardi.process_engine.action.v1.consents.add_consent_action.plugin": {
        'consents': None},
    "tracardi.process_engine.action.v1.consents.require_consents_action.plugin": {
        'consent_ids': [],
        'require_all': False},
    "tracardi.process_engine.action.v1.pro.scheduler.plugin": None,
    "tracardi.process_engine.action.v1.connectors.rabbitmq.publish.plugin": {
        'queue': {
            'auto_declare': True,
            'compression': None,
            'name': None,
            'queue_type': 'direct',
            'routing_key': None,
            'serializer': 'json'
        },
        'source': {
            'id': None}
    },
    "tracardi.process_engine.action.v1.flow.postpone_event.plugin": None
}


async def add_plugins():
    return await install_plugins(installed_plugins)
