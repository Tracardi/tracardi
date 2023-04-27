from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    session: str = 'always'

