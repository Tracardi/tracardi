from enum import Enum


class ProductionDraft(str, Enum):
    production = "production"
    draft = "draft"
