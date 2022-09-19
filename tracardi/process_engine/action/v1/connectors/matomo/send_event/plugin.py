from tracardi.process_engine.action.v1.connectors.matomo.client import MatomoClient, MatomoClientException
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .service.page_performance import PerformanceValueGetter
from .model.config import Config, MatomoPayload
from tracardi.service.notation.dict_traverser import DictTraverser
import hashlib


def validate(config: dict) -> Config:
    return Config(**config)


class SendEventToMatomoAction(ActionRunner):

    client: MatomoClient
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.client = MatomoClient(**resource.credentials.get_credentials(self))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)

        if 'session@context.screen.local.height' in dot and 'session@context.screen.local.width' in dot:
            res = f"{dot['session@context.screen.local.height']}x{dot['session@context.screen.local.width']}"
        else:
            res = None

        if "session@context.browser.local.browser.userAgent" in dot:
            ua = dot["session@context.browser.local.browser.userAgent"]
        else:
            ua = None

        if "session@context.browser.local.browser.language" in dot:
            lang = dot["session@context.browser.local.browser.language"]
        else:
            lang = None

        if "session@operation.new" in dot and dot["session@operation.new"] is True:
            new_visit = 1
        else:
            new_visit = 0

        perf_data_service = PerformanceValueGetter(dot)

        response_start = perf_data_service.get_performance_value("responseStart")
        redirect_start = perf_data_service.get_performance_value("redirectStart")
        dom_complete = perf_data_service.get_performance_value("domComplete")
        response_end = perf_data_service.get_performance_value("responseEnd")
        dom_content_loaded = perf_data_service.get_performance_value("domContentLoadedEventStart")
        dom_loading = perf_data_service.get_performance_value("domContentLoadedEventStart")
        load_event_start = perf_data_service.get_performance_value("loadEventStart")
        load_event_end = perf_data_service.get_performance_value("loadEventEnd")
        request_start = perf_data_service.get_performance_value("requestStart")

        data = MatomoPayload(
            cip=self.event.request.get("ip", None),
            idsite=self.config.site_id,
            action_name=self.event.type,
            url=self.event.context.get("page", {"url": None}).get("url", None),
            _id=self.profile.id.replace("-", "")[0:16],
            urlref=dot[self.config.url_ref] if self.config.url_ref is not None else None,
            _idvc=self.profile.metadata.time.visit.count,
            _viewts=self.profile.metadata.time.visit.last.timestamp() if self.profile.metadata.time.visit.last
                                                                         is not None else None,
            _idts=self.profile.metadata.time.insert,
            _rcn=dot[self.config.rcn] if self.config.rcn is not None else None,
            _rck=dot[self.config.rck] if self.config.rck is not None else None,
            res=res,
            ua=ua,
            lang=lang,
            uid=self.profile.id.replace("-", "")[0:16],
            new_visit=new_visit,
            search=dot[self.config.search_keyword] if self.config.search_keyword is not None else None,
            search_cat=dot[self.config.search_category] if self.config.search_category is not None else None,
            search_count=dot[self.config.search_results_count] if self.config.search_results_count is not None
            else None,
            pv_id=self.make_pv_id(),
            idgoal=int(dot[self.config.goal_id]) if self.config.goal_id is not None else None,
            revenue=float(dot[self.config.revenue]) if self.config.revenue is not None else None,
            gt_ms=int(response_end - request_start) if 0 not in (request_start, response_end) else None,
            dimensions=traverser.reshape(self.config.dimensions),
            pf_net=int(response_start - redirect_start) if 0 not in (response_start, redirect_start) else None,
            pf_srv=int(dom_complete - response_start) if 0 not in (dom_complete, response_start) else None,
            pf_tfr=int(response_end - response_start) if 0 not in (response_end, response_start) else None,
            pf_dm2=int(dom_content_loaded - dom_complete) if 0 not in (dom_complete, dom_content_loaded) else None,
            pf_dm1=int(dom_content_loaded - dom_loading) if 0 not in (dom_content_loaded, dom_loading) else None,
            pf_onl=int(load_event_end - load_event_start) if 0 not in (load_event_end, load_event_start) else None
        )

        try:
            await self.client.send_event(data)
            return Result(port="response", value=payload)

        except MatomoClientException as e:
            return Result(port="error", value={"message": str(e)})

    def make_pv_id(self) -> str:
        md5_hash = hashlib.md5(
            f'{self.session.id}{self.event.context.get("page", {"url": ""}).get("url", "")}'.encode()
        )
        characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

        def to_base(n, b):
            return "0" if not n else to_base(n // b, b).lstrip("0") + characters[n % b]

        result = to_base(int(md5_hash.hexdigest()[0:8], base=16), 62)

        return "0" * (6 - len(result)) + result


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SendEventToMatomoAction',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            # manual,
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "site_id": None,
                "url_ref": "event@context.page.referer.host",
                "rcn": "session@context.utm.campaign",
                "rck": "session@context.utm.term",
                "search_keyword": None,
                "search_category": None,
                "search_results_count": None,
                "goal_id": None,
                "revenue": None,
                "dimensions": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Matomo resource",
                                description="Please select your Matomo resource, containing Matomo URL and token.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "matomo"})
                            ),
                            FormField(
                                id="site_id",
                                name="Site ID",
                                description="Please provide a site ID, which will be used by Matomo to assign sent "
                                            "event to given site. This ID should be an integer.",
                                component=FormComponent(type="text", props={"label": "Site ID"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="Marketing configuration",
                        description="This part is optional and configured with default data.",
                        fields=[
                            FormField(
                                id="url_ref",
                                name="Referrer URL",
                                description="If you have an URL that shows how the profile got to your website, you can"
                                            "include it in information sent to Matomo, by providing a path to it below."
                                            " This field is optional.",
                                component=FormComponent(type="dotPath", props={"label": "Referrer URL"})
                            ),
                            FormField(
                                id="rcn",
                                name="Campaign name",
                                description="If you know by which campaign the profile got to your website, you can "
                                            "provide a path to its name. This field is optional.",
                                component=FormComponent(type="dotPath", props={"label": "Campaign name"})
                            ),
                            FormField(
                                id="rck",
                                name="Campaign keyword",
                                description="If you know the campaign that led the user to your website, you can "
                                            "provide a path to a keyword associated with that campaign. This field "
                                            "is optional",
                                component=FormComponent(type="dotPath", props={"label": "Campaign keyword"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="Search configuration",
                        fields=[
                            FormField(
                                id="search_keyword",
                                name="Search keyword",
                                description="If you know that the profile has searched for something on you page, you "
                                            "can provide a path to the field containing search keyword typed by them. "
                                            "This field is optional.",
                                component=FormComponent(type="dotPath", props={"label": "Search keyword"})
                            ),
                            FormField(
                                id="search_category",
                                name="Search category",
                                description="If you know the category of the search performed by profile, you can "
                                            "include this category by providing a path to it. This field is also "
                                            "optional.",
                                component=FormComponent(type="dotPath", props={"label": "Search category"})
                            ),
                            FormField(
                                id="search_results_count",
                                name="Number of search results",
                                description="If you know how many results were returned for performed search, you can "
                                            "include this number by providing a path to it. This field is optional.",
                                component=FormComponent(type="dotPath", props={"label": "Result"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="Goal configuration",
                        fields=[
                            FormField(
                                id="goal_id",
                                name="ID of the goal",
                                description="If you know about presence of one of the goals previously defined in "
                                            "Matomo, you can include this goal's ID by providing a path to it, or "
                                            "setting it to one value. This field is optional.",
                                component=FormComponent(type="dotPath", props={"label": "Goal ID"})
                            ),
                            FormField(
                                id="revenue",
                                name="Revenue of the goal",
                                description="If you know the amount of revenue generated by the goal, you can include "
                                            "this number (integer or float value) by providing a path to it. This field"
                                            " is also optional.",
                                component=FormComponent(type="dotPath", props={"label": "Revenue"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="Dimensions",
                        fields=[
                            FormField(
                                id="dimensions",
                                name="Custom dimensions",
                                description="If you use Matomo with Custom Dimensions plugin, you can include up to "
                                            "1000 custom dimensions, previously defined in Matomo. To do it, just type "
                                            "the 'dimension' keyword with dimension ID at the end as the key, and path "
                                            "to this dimension's value as the value. "
                                            "(e.g. dimension17 - profile@pii.name)",
                                component=FormComponent(type="keyValueList", props={"label": "Dimensions"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Register event',
            desc='Sends current event to Matomo.',
            icon='matomo',
            brand='Matomo',
            group=["Matomo"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns payload if everything is OK."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
