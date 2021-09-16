import tracardi.service.storage.drivers.elastic.profile
import tracardi.service.storage.drivers.elastic.session
import tracardi.service.storage.drivers.elastic.event
import tracardi.service.storage.drivers.elastic.flow
import tracardi.service.storage.drivers.elastic.rule
import tracardi.service.storage.drivers.elastic.segment
import tracardi.service.storage.drivers.elastic.plugin
import tracardi.service.storage.drivers.elastic.debug_info
import tracardi.service.storage.drivers.elastic.resource
import tracardi.service.storage.drivers.elastic.action
import tracardi.service.storage.drivers.elastic.console_log
import tracardi.service.storage.drivers.elastic.task
import tracardi.service.storage.drivers.elastic.api_instance


class ElasticDriver:

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
    def flow(self):
        return tracardi.service.storage.drivers.elastic.flow

    @property
    def rule(self):
        return tracardi.service.storage.drivers.elastic.rule

    @property
    def segment(self):
        return tracardi.service.storage.drivers.elastic.segment

    @property
    def plugin(self):
        return tracardi.service.storage.drivers.elastic.plugin

    @property
    def debug_info(self):
        return tracardi.service.storage.drivers.elastic.debug_info

    @property
    def resource(self):
        return tracardi.service.storage.drivers.elastic.resource

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
    def api_instance(self):
        return tracardi.service.storage.drivers.elastic.api_instance
