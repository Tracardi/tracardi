import asyncio
import logging
import os
from collections import defaultdict

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.module_loader import pip_install, load_callable, import_package
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.domain.register import Plugin


__local_dir = os.path.dirname(__file__)
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def add_plugin(module, install=False, upgrade=False):

    try:

        # upgrade
        if install and upgrade:
            pip_install(module.split(".")[0], upgrade=True)

        try:
            # import
            module = import_package(module)
        except ImportError as e:
            # install
            if install:
                pip_install(module.split(".")[0])
                module = import_package(module)
            else:
                raise e

        # loads and installs dependencies
        plugin = load_callable(module, 'register')
        plugin_data = plugin()  # type: Plugin

        if len(plugin_data.spec.inputs) > 1:
            raise ValueError(
                "Node can not have more then 1 input port. Found {} that is {}".format(
                    plugin_data.spec.inputs,
                    len(plugin_data.spec.inputs)
                ))

        # Action plugin id is a hash of its module and className

        await asyncio.sleep(0)
        logger.info(f"Module `{plugin_data.spec.module}` was REGISTERED.")
        return await storage.driver.action.save_plugin(plugin_data)

    except ModuleNotFoundError as e:
        logger.error(f"Module `{module}` was NOT INSTALLED as it raised an error `{str(e)}`.")


async def add_plugins():
    result = defaultdict(list)
    plugins = [
        'tracardi.process_engine.action.v1.debug_payload_action',
        'tracardi.process_engine.action.v1.flow.start.start_action',
        'tracardi.process_engine.action.v1.flow.property_exists.plugin',
        'tracardi.process_engine.action.v1.end_action',
        'tracardi.process_engine.action.v1.raise_error_action',
        'tracardi.process_engine.action.v1.inject_action',

        'tracardi.process_engine.action.v1.increase_views_action',
        'tracardi.process_engine.action.v1.increase_visits_action',
        'tracardi.process_engine.action.v1.increment_action',
        'tracardi.process_engine.action.v1.decrement_action',

        'tracardi.process_engine.action.v1.if_action',
        'tracardi.process_engine.action.v1.new_visit_action',
        'tracardi.process_engine.action.v1.new_profile_action',
        'tracardi.process_engine.action.v1.template_action',

        'tracardi.process_engine.action.v1.detect_client_agent_action',
        'tracardi.process_engine.action.v1.misc.uuid4_action',
        'tracardi.process_engine.action.v1.misc.hash_value_action',

        'tracardi.process_engine.action.v1.traits.copy_trait_action',
        'tracardi.process_engine.action.v1.traits.append_trait_action',
        'tracardi.process_engine.action.v1.traits.cut_out_trait_action',
        'tracardi.process_engine.action.v1.traits.delete_trait_action',
        'tracardi.process_engine.action.v1.traits.auto_merge_properties_to_profile_action',
        'tracardi.process_engine.action.v1.traits.assign_condition_result.plugin',

        'tracardi.process_engine.action.v1.operations.merge_profiles_action',
        'tracardi.process_engine.action.v1.operations.segment_profile_action',
        'tracardi.process_engine.action.v1.operations.update_profile_action',
        'tracardi.process_engine.action.v1.operations.update_event_action',
        'tracardi.process_engine.action.v1.operations.update_session_action',
        'tracardi.process_engine.action.v1.calculator_action',
        'tracardi.process_engine.action.v1.mapping_action',
        'tracardi.process_engine.action.v1.return_random_element_action',
        'tracardi.process_engine.action.v1.log_action',
        'tracardi.process_engine.action.v1.scrapper.xpath.plugin',
        'tracardi.process_engine.action.v1.operations.threshold.plugin',

        # Geo
        'tracardi.process_engine.action.v1.geo.fence.circular.plugin',
        'tracardi.process_engine.action.v1.geo.distance.plugin',


        # Plugins
        'tracardi.process_engine.action.v1.traits.reshape_payload_action',
        'tracardi.process_engine.action.v1.detect_client_agent_action',

        'tracardi.process_engine.action.v1.events.event_counter.plugin',
        'tracardi.process_engine.action.v1.json_schema_validation_action',

        # String
        'tracardi.process_engine.action.v1.strings.string_operations.plugin',
        'tracardi.process_engine.action.v1.strings.regex_match.plugin',
        'tracardi.process_engine.action.v1.strings.regex_validator.plugin',
        'tracardi.process_engine.action.v1.strings.string_validator.plugin',
        'tracardi.process_engine.action.v1.strings.string_splitter.plugin',
        'tracardi.process_engine.action.v1.strings.url_parser.plugin',
        'tracardi.process_engine.action.v1.strings.regex_replace.plugin',

        # Time
        'tracardi.process_engine.action.v1.time.sleep_action',
        'tracardi.process_engine.action.v1.time.today_action',
        'tracardi.process_engine.action.v1.time.day_night.plugin',
        'tracardi.process_engine.action.v1.time.local_time_span.plugin',
        'tracardi.process_engine.action.v1.time.time_difference.plugin',

        # UX
        'tracardi.process_engine.action.v1.ux.snackbar.plugin',
        'tracardi.process_engine.action.v1.ux.consent.plugin',
        'tracardi.process_engine.action.v1.ux.cta_message.plugin',
        'tracardi.process_engine.action.v1.ux.rating_popup.plugin',
        'tracardi.process_engine.action.v1.ux.question_popup.plugin',
        'tracardi.process_engine.action.v1.ux.contact_popup.plugin',

        # Connectors
        'tracardi.process_engine.action.v1.connectors.html.fetch.plugin',
        'tracardi.process_engine.action.v1.connectors.api_call.plugin',
        'tracardi.process_engine.action.v1.connectors.smtp_call.plugin',
        'tracardi.process_engine.action.v1.segments.profile_segmentation.plugin',
        'tracardi.process_engine.action.v1.converters.data_to_json.plugin',
        'tracardi.process_engine.action.v1.converters.json_to_data.plugin',
        'tracardi.process_engine.action.v1.connectors.mailchimp.transactional_email.plugin',
        'tracardi.process_engine.action.v1.connectors.elasticsearch.query.plugin',
        'tracardi.process_engine.action.v1.connectors.mailchimp.add_to_audience.plugin',
        'tracardi.process_engine.action.v1.connectors.mailchimp.remove_from_audience.plugin',
        'tracardi.process_engine.action.v1.connectors.trello.add_card_action.plugin',
        'tracardi.process_engine.action.v1.connectors.trello.delete_card_action.plugin',
        'tracardi.process_engine.action.v1.connectors.trello.move_card_action.plugin',
        'tracardi.process_engine.action.v1.connectors.trello.add_member_action.plugin',
        'tracardi.process_engine.action.v1.connectors.amplitude.send_events.plugin',
        'tracardi.process_engine.action.v1.connectors.mongo.query.plugin',
        'tracardi.process_engine.action.v1.connectors.full_contact.person_enrich.plugin',
        'tracardi.process_engine.action.v1.connectors.zapier.webhook.plugin',
        'tracardi.process_engine.action.v1.connectors.pushover.push.plugin',
        'tracardi.process_engine.action.v1.connectors.discord.push.plugin',

        'tracardi.process_engine.action.v1.connectors.maxmind.geoip.plugin',
        'tracardi.process_engine.action.v1.connectors.mysql.query.plugin',
        'tracardi.process_engine.action.v1.connectors.postgresql.query.plugin',
        'tracardi.process_engine.action.v1.connectors.weather.msn_weather.plugin',
        'tracardi.process_engine.action.v1.connectors.aws.sqs.plugin',
        'tracardi.process_engine.action.v1.connectors.meaningcloud.sentiment_analysis.plugin',
        'tracardi.process_engine.action.v1.connectors.meaningcloud.language_detection.plugin',
        'tracardi.process_engine.action.v1.connectors.meaningcloud.text_classification.plugin',
        'tracardi.process_engine.action.v1.connectors.oauth2_token.plugin',
        'tracardi.process_engine.action.v1.connectors.slack.send_message.plugin',
        'tracardi.process_engine.action.v1.connectors.google.sheets.modify.plugin',
        'tracardi.process_engine.action.v1.connectors.meaningcloud.deep_categorization.plugin',
        'tracardi.process_engine.action.v1.connectors.meaningcloud.corporate_reputation.plugin',
        'tracardi.process_engine.action.v1.connectors.meaningcloud.topics_extraction.plugin',
        'tracardi.process_engine.action.v1.connectors.meaningcloud.summarization.plugin',
        'tracardi.process_engine.action.v1.connectors.influxdb.send.plugin',
        'tracardi.process_engine.action.v1.connectors.influxdb.fetch.plugin',
        'tracardi.process_engine.action.v1.connectors.mixpanel.send.plugin',
        'tracardi.process_engine.action.v1.connectors.mixpanel.fetch_funnel.plugin',
        'tracardi.process_engine.action.v1.connectors.mautic.add_contact.plugin',
        'tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_id.plugin',
        'tracardi.process_engine.action.v1.connectors.mautic.fetch_contact_by_email.plugin',
        'tracardi.process_engine.action.v1.connectors.mautic.edit_points.plugin',
        'tracardi.process_engine.action.v1.connectors.mautic.add_remove_segment.plugin',
        'tracardi.process_engine.action.v1.connectors.airtable.send_record.plugin',
        'tracardi.process_engine.action.v1.connectors.airtable.fetch_records.plugin',
        'tracardi.process_engine.action.v1.connectors.matomo.send_event.plugin',
        'tracardi.process_engine.action.v1.connectors.civi_crm.add_contact.plugin',
        'tracardi.process_engine.action.v1.connectors.active_campaign.fetch_by_email.plugin',
        'tracardi.process_engine.action.v1.connectors.active_campaign.add_contact.plugin',
        'tracardi.process_engine.action.v1.connectors.salesforce.marketing_cloud.send.plugin',

        # Internal
        'tracardi.process_engine.action.v1.internal.assign_profile_id.plugin',
        'tracardi.process_engine.action.v1.internal.event_source_fetcher.plugin',
        'tracardi.process_engine.action.v1.internal.inject_event.plugin',
        'tracardi.process_engine.action.v1.internal.inject_profile.plugin',
        'tracardi.process_engine.action.v1.traits.condition_set.plugin',
        'tracardi.process_engine.action.v1.internal.query_string.plugin',
        'tracardi.process_engine.action.v1.operations.reduce_array.plugin',
        'tracardi.process_engine.action.v1.internal.get_prev_event.plugin',
        'tracardi.process_engine.action.v1.internal.get_prev_session.plugin',
        'tracardi.process_engine.action.v1.operations.write_to_memory.plugin',
        'tracardi.process_engine.action.v1.operations.read_from_memory.plugin',


        # Metrics
        'tracardi.process_engine.action.v1.metrics.key_counter.plugin',
        # 'tracardi.process_engine.action.v1.microservice.profile_metrics',

        # Consents
        'tracardi.process_engine.action.v1.consents.add_consent_action.plugin',
        'tracardi.process_engine.action.v1.consents.require_consents_action.plugin',

        # Tracardi Pro
        'tracardi.process_engine.action.v1.pro.scheduler.plugin',
        'tracardi.process_engine.action.v1.connectors.rabbitmq.publish.plugin',
        'tracardi.process_engine.action.v1.flow.postpone_event.plugin',

    ]
    for plugin in plugins:
        status = await add_plugin(plugin, install=False, upgrade=False)
        if status is not None:
            result["registered"].append(plugin)
        else:
            result["error"].append(plugin)

    return result
