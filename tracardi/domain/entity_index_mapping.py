from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class EntityRelation(BaseModel):
    index: str
    alias: Optional[str] = None
    pk: str


class EntityPropertyMeta(BaseModel):
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    type: Optional[str] = None
    required: Optional[bool] = False
    rel: Optional[List[EntityRelation]] = None


class EntityMappingMeta(BaseModel):
    name: str
    description: Optional[str] = ""
    version: str
    part_of: List[str] = []
    pk: Optional[str] = None
    properties: Dict[str, EntityPropertyMeta] = []


class EntityMappings(BaseModel):
    meta: EntityMappingMeta = Field(..., alias='_meta')
    dynamic: Optional[str] = "strict"
    properties: Dict[str, dict]

    def add_property_meta(self, field: str, property_meta: EntityPropertyMeta):
        self.meta.properties[field] = property_meta

    def add_property(self, field: str, definition: dict, property_meta: EntityPropertyMeta):
        self.properties[field] = definition
        self.add_property_meta(field, property_meta)


class EntityIndexMapping(BaseModel):
    settings: Optional[dict] = {}
    mappings: EntityMappings
    aliases: Optional[dict] = {}
