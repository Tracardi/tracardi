import json
import os

from app import config
from app.globals.elastic_client import elastic_client

__local_dir = os.path.dirname(__file__)


def create_indices():
    es = elastic_client()
    for key, index in config.index.items():

        map_file = 'mappings/default-dynamic-index.json'

        with open(os.path.join(__local_dir, map_file)) as file:
            map = json.load(file)
            if not es.exists_index(index):
                es.create_index(index, map)


