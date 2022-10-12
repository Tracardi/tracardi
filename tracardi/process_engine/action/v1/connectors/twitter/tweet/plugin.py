from tracardi.domain.resources.twitter_resrouce import TwitterResourceCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormComponent, FormField, MetaData, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
import tweepy
from .model.config import Configuration


def validate(config: dict):
    return Configuration(**config)


class TwitterTweetAction(ActionRunner):
    credentials: TwitterResourceCredentials
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=TwitterResourceCredentials)

    async def run(self, payload: dict, in_edge=None) -> Result:

        authorization = tweepy.OAuthHandler(
            self.credentials.consumer_key,
            self.credentials.consumer_secret
        )

        authorization.set_access_token(
            self.credentials.access_token,
            self.credentials.access_token_secret
        )

        tweet_api = tweepy.API(authorization)
        tweet = self.config.tweet

        try:
            tweet_api.update_status(tweet)
            return Result(port='response', value="Tweet added successfully")
        except tweepy.errors.HTTPException as e:
            return Result(port="error", value={
                "message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TwitterTweetAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            verions='0.7.3',
            license='MIT',
            author='Mateusz Zitaruk',
            manual='twitter_tweet_action',
            init={
                'source': {
                    'id': '',
                    'name': ''
                },
                'tweet': ''
            },
            form=Form(groups=[
                FormGroup(
                    name='Twitter resource',
                    fields=[
                        FormField(
                            id='source',
                            name='Twitter resource',
                            description='Select Twitter resource. Credentials from selected resource will be used '
                                        'to authorize your account.',
                            component=FormComponent(type='resource', props={
                                'label': 'resource',
                                'tag': 'twitter'
                            }
                                                    )
                        ),
                        FormField(
                            id='tweet',
                            name='Tweet',
                            description='Please enter the content of your tweet.',
                            component=FormComponent(
                                type='text',
                                props={
                                    'label': 'Tweet'
                                }
                            )
                        )
                    ]
                )
            ]
            )
        ),
        metadata=MetaData(
            name='Twitter tweet',
            desc='Create and send tweet to your twitter wall.',
            icon='twitter',
            group=['Connectors'],
            documentation=Documentation(
                inputs={
                    'payload': PortDoc(desc='This port takes payload object.')
                },
                outputs={
                    'response': PortDoc(desc='This port returns response status.'),
                    'error': PortDoc(desc='This port returns error object.')
                }
            )
        )
    )
