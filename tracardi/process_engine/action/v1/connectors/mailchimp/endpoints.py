from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resources.token import Token
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from tracardi.process_engine.action.v1.connectors.mailchimp.service.mailchimp_audience_editor import MailChimpAudienceEditor
from tracardi.service.domain import resource as resource_db


class AudienceConfig(PluginConfig):
    source: NamedEntity

class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_audiences(config: dict):
        config = AudienceConfig(**config)
        if config.source.is_empty():
            raise ValueError("Resource not set.")

        resource = await resource_db.load(config.source.id)
        creds = Token(**resource.credentials.production)
        client = MailChimpAudienceEditor(
            creds.token,
            2
        )
        result = await client.get_all_audience_ids()

        return {
            "total": len(result),
            "result": result
        }


