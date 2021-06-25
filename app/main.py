import logging
import os
from time import sleep

import elasticsearch
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles
from .api import token_endpoint, rule_endpoint, source_endpoint, consent_endpoint, event_endpoint, \
    profile_endpoint, flow_endpoint, generic_endpoint, project_endpoint, credentials_endpoint, segments_endpoint, \
    tql_endpoint, graphql_endpoint
from .domain.flow_action_plugins import FlowActionPlugins
from .event_server import event_server_endpoint
from app.service.storage.elastic import Elastic
from .setup.indices_setup import create_indices

logging.basicConfig(level=logging.INFO)

_local_dir = os.path.dirname(__file__)

tags_metadata = [
    {
        "name": "profile",
        "description": "Manage profiles. Read more about core concepts of TRACARDI in documentation.",
        "externalDocs": {
            "description": "Profile external docs",
            "url": "https://github/atompie/docs/en/docs/core_concepts",
        },
    },
    {
        "name": "source",
        "description": "Manage data sources. Read more about core concepts of TRACARDI in documentation.",
        "externalDocs": {
            "description": "Source external docs",
            "url": "https://github/atompie/docs/en/docs/core_concepts",
        },
    },
    {
        "name": "rule",
        "description": "Manage flow rule triggers. Read more about core concepts of TRACARDI in documentation.",
        "externalDocs": {
            "description": "Rule external docs",
            "url": "https://github/atompie/docs/en/docs/core_concepts",
        },
    },
    {
        "name": "flow",
        "description": "Manage flows. Read more about core concepts of TRACARDI in documentation.",
        "externalDocs": {
            "description": "Flows external docs",
            "url": "https://github/atompie/docs/en/docs/core_concepts",
        },
    },
    {
        "name": "event",
        "description": "Manage events. Read more about core concepts of TRACARDI in documentation.",
        "externalDocs": {
            "description": "Events external docs",
            "url": "https://github/atompie/docs/en/docs/core_concepts",
        },
    },
    {
        "name": "authorization",
        "description": "OAuth authorization.",
    },
    {
        "name": "event server",
        "description": "Read more about TRACARDI event server in documentation.",
        "externalDocs": {
            "description": "External docs",
            "url": "https://github/atompie/docs/en/docs/event_server",
        },
    }
]

application = FastAPI(
    title="Tracardi Customer Data Platform Project",
    description="TRACARDI open-source customer data platform offers you excellent control over your customer data with its broad set of features",
    version="0.4.0",
    openapi_tags=tags_metadata
)
application.mount("/tracker",
                  StaticFiles(
                      html=True,
                      directory=os.path.join(_local_dir, "tracker")),
                  name="tracker")

application.mount("/manual",
                  StaticFiles(
                      html=True,
                      directory=os.path.join(_local_dir, "../manual")),
                  name="manual")

application.include_router(graphql_endpoint.router)
application.include_router(tql_endpoint.router)
application.include_router(segments_endpoint.router)
application.include_router(credentials_endpoint.router)
application.include_router(project_endpoint.router)
application.include_router(event_server_endpoint.router)
application.include_router(source_endpoint.router)
application.include_router(rule_endpoint.router)
application.include_router(flow_endpoint.router)
application.include_router(consent_endpoint.router)
application.include_router(event_endpoint.router)
application.include_router(profile_endpoint.router)
application.include_router(token_endpoint.router)
application.include_router(generic_endpoint.router)

application.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@application.on_event("startup")
async def app_starts():
    while True:
        try:
            await create_indices()
            break
        except elasticsearch.exceptions.ConnectionError:
            sleep(2)


@application.on_event("shutdown")
async def app_shutdown():
    elastic = Elastic.instance()
    await elastic.close()


@application.post("/json")
async def track(r: Request):
    return await r.json()


@application.get("/action/plugins")
async def plugins():
    plugins = FlowActionPlugins()
    return await plugins.bulk().load()
