import tracardi.service.storage.drivers.elastic.profile
import tracardi.service.storage.drivers.elastic.session
import tracardi.service.storage.drivers.elastic.event
import tracardi.service.storage.drivers.elastic.flow
import tracardi.service.storage.drivers.elastic.rule
import tracardi.service.storage.drivers.elastic.segment
import tracardi.service.storage.drivers.elastic.debug_info
import tracardi.service.storage.drivers.elastic.resource
import tracardi.service.storage.drivers.elastic.action
import tracardi.service.storage.drivers.elastic.console_log
import tracardi.service.storage.drivers.elastic.task
import tracardi.service.storage.drivers.elastic.api_instance
import tracardi.service.storage.drivers.elastic.log
import tracardi.service.storage.drivers.elastic.raw
import tracardi.service.storage.drivers.elastic.consent_type
import tracardi.service.storage.drivers.elastic.user
import tracardi.service.storage.drivers.elastic.event_source
import tracardi.service.storage.drivers.elastic.pro
import tracardi.service.storage.drivers.elastic.value_threshold
import tracardi.service.storage.drivers.elastic.destination
import tracardi.service.storage.drivers.elastic.user_log
import tracardi.service.storage.drivers.elastic.import_config
import tracardi.service.storage.drivers.elastic.version
import tracardi.service.storage.drivers.elastic.snapshot
import tracardi.service.storage.drivers.elastic.entity
import tracardi.service.storage.drivers.elastic.report
import tracardi.service.storage.drivers.elastic.live_segment
import tracardi.service.storage.drivers.elastic.event_reshaping
import tracardi.service.storage.drivers.elastic.event_validation
import tracardi.service.storage.drivers.elastic.system
import tracardi.service.storage.drivers.elastic.event_management
import tracardi.service.storage.drivers.elastic.event_redirect
import tracardi.service.storage.drivers.elastic.bridge


class ElasticDriver:

    @property
    def value_threshold(self):
        return tracardi.service.storage.drivers.elastic.value_threshold

    @property
    def pro(self):
        return tracardi.service.storage.drivers.elastic.pro

    @property
    def system(self):
        return tracardi.service.storage.drivers.elastic.system

    @property
    def raw(self):
        return tracardi.service.storage.drivers.elastic.raw

    @property
    def profile(self):
        return tracardi.service.storage.drivers.elastic.profile

    @property
    def session(self):
        return tracardi.service.storage.drivers.elastic.session

    @property
    def event(self):
        return tracardi.service.storage.drivers.elastic.event

    @property
    def bridge(self):
        return tracardi.service.storage.drivers.elastic.bridge

    @property
    def event_management(self):
        return tracardi.service.storage.drivers.elastic.event_management

    @property
    def flow(self):
        return tracardi.service.storage.drivers.elastic.flow

    @property
    def rule(self):
        return tracardi.service.storage.drivers.elastic.rule

    @property
    def segment(self):
        return tracardi.service.storage.drivers.elastic.segment

    @property
    def live_segment(self):
        return tracardi.service.storage.drivers.elastic.live_segment

    @property
    def debug_info(self):
        return tracardi.service.storage.drivers.elastic.debug_info

    @property
    def resource(self):
        return tracardi.service.storage.drivers.elastic.resource

    @property
    def event_source(self):
        return tracardi.service.storage.drivers.elastic.event_source

    @property
    def event_redirect(self):
        return tracardi.service.storage.drivers.elastic.event_redirect

    @property
    def action(self):
        return tracardi.service.storage.drivers.elastic.action

    @property
    def console_log(self):
        return tracardi.service.storage.drivers.elastic.console_log

    @property
    def task(self):
        return tracardi.service.storage.drivers.elastic.task

    @property
    def api_instance(self) -> tracardi.service.storage.drivers.elastic.api_instance:
        return tracardi.service.storage.drivers.elastic.api_instance

    @property
    def log(self):
        return tracardi.service.storage.drivers.elastic.log

    @property
    def consent_type(self):
        return tracardi.service.storage.drivers.elastic.consent_type

    @property
    def user(self) -> tracardi.service.storage.drivers.elastic.user:
        return tracardi.service.storage.drivers.elastic.user

    @property
    def destination(self) -> tracardi.service.storage.drivers.elastic.destination:
        return tracardi.service.storage.drivers.elastic.destination

    @property
    def user_log(self) -> tracardi.service.storage.drivers.elastic.user_log:
        return tracardi.service.storage.drivers.elastic.user_log

    @property
    def import_config(self) -> tracardi.service.storage.drivers.elastic.import_config:
        return tracardi.service.storage.drivers.elastic.import_config

    @property
    def version(self) -> tracardi.service.storage.drivers.elastic.version:
        return tracardi.service.storage.drivers.elastic.version

    @property
    def snapshot(self):
        return tracardi.service.storage.drivers.elastic.snapshot

    @property
    def entity(self):
        return tracardi.service.storage.drivers.elastic.entity

    @property
    def report(self):
        return tracardi.service.storage.drivers.elastic.report

    @property
    def event_reshaping(self):
        return tracardi.service.storage.drivers.elastic.event_reshaping

    @property
    def event_validation(self):
        return tracardi.service.storage.drivers.elastic.event_validation
