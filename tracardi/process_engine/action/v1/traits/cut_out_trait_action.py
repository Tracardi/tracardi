from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    FormFieldValidation
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class CutOutTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'trait' not in kwargs:
            raise ValueError("Please define trait in config section.")

        if kwargs['trait'] == 'undefined':
            raise ValueError("Please define trait in config section. It has default value of undefined.")

        self.property = kwargs['trait']

    async def run(self, payload: dict):

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)
        return Result(port="trait", value=dot[self.property])


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.cut_out_trait_action',
            className='CutOutTraitAction',
            inputs=['payload'],
            outputs=["trait"],
            init={
                "trait": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Cut data to payload",
                    fields=[
                        FormField(
                            id="trait",
                            name="Path to data",
                            description="Provide path to field that you would like to return as output payload. "
                                        "E.g. event@session.context.browser.browser.userAgent",
                            component=FormComponent(type="dotPath", props={"label": "Field path"}),
                            validation=FormFieldValidation(
                                regex=r"^[a-zA-Z0-9\@\.\-_]+$",
                                message="This field must be in Tracardi dot path format."
                            )
                        )
                    ]
                )
            ]),
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Cut out trait',
            desc='Returns defined property from payload.',
            type='flowNode',
            width=200,
            height=100,
            icon='property',
            group=["Data processing"]
        )
    )
