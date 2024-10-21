from lxml import etree
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.runner import ActionRunner
from pydantic import field_validator
from tracardi.domain.profile import Profile
from tracardi.service.tracardi_http_client import HttpClient

class Configuration(PluginConfig):
    sitemap_path: str

    @field_validator('sitemap_path')
    @classmethod
    def sitemap_path_must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("Sitemap path must not be empty.")
        return value

def validate(config: dict):
    return Configuration(**config)

class SitemapAction(ActionRunner):
    
    config: Configuration
    
    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)
        urls = []
        
        try:
            
            sitemap_path=dot[self.config.sitemap_path]
            content = await self.fetch_sitemap(sitemap_path)
            sitemap_urls = await self.process_sitemap_index(content)
            
            for sitemap_url in sitemap_urls:
                content = await self.fetch_sitemap(sitemap_url)
                result = await self.process_sitemap(content)
                urls.extend(result)  

            return Result(port='result', value={'urls':urls})

        except Exception as e:
            return Result(value={"message": str(e)}, port="error")  
        
    async def process_sitemap_index(self, sitemap_index_content):
        sitemap_urls = []
        if sitemap_index_content is None:
            print("Error: sitemap_index_content is None.")
            return sitemap_urls
        try:
            root = etree.fromstring(sitemap_index_content.encode('utf-8'))
            for sitemap in root.findall(".//{*}sitemap"):
                loc = sitemap.find(".//{*}loc")
                if loc is not None and loc.text is not None: 
                    sitemap_urls.append(loc.text)
        except Exception as e:
            print(f"Error processing sitemap index: {e}")
            
        return sitemap_urls

    async def fetch_sitemap(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        async with HttpClient(3, [200], headers=headers) as client:
            async with client.get(url=url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Error fetching sitemap: {response.status}")
                    return None

    async def process_sitemap(self,sitemap_content):
        urls = []
        try:
            root = etree.fromstring(sitemap_content.encode('utf-8'))
            namespace = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for url in root.findall("sitemap:url", namespaces=namespace):
                loc = url.find("sitemap:loc", namespaces=namespace)
                if loc is not None:
                    urls.append(loc.text)                    
        except Exception as e:
            print(f"Error processing sitemap: {e}")
        return urls

def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=SitemapAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version="1.0.3",  
            init={
                "sitemap_path": "",  
            },
            form=Form(groups=[
                FormGroup(
                    name="Sitemap configuration",
                    fields=[
                        FormField(
                            id="sitemap_path",
                            name="Sitemap Path",
                            description="The URL where the sitemap can be found.",
                            component=FormComponent(type="dotPath", props={
                                "label": "Sitemap Path"
                            })
                        ),
                    ])
            ]),
            license="MIT",
            author="Matt Cameron",
            manual="sitemap",  

        ),
        metadata=MetaData(
            name='Sitemap',
            desc='Fetches a list URLs from a sitemap.',
            icon='Sitemap',
            group=['Sitemaps'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns response from Sitemap service."),
                    "error": PortDoc(desc="Returns error message if plugin fails.")
                }
            )
        )
    )

