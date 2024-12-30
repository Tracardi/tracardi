from typing import Optional, List, Callable
from pydantic import field_validator, BaseModel
from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext
from tracardi.process_engine.tql.condition import Condition
from tracardi.common.security.encrypt.secrets import b64_decoder, b64_encoder
from tracardi.service.module_loader import load_callable, import_package


class DestinationConfig(BaseModel):
    package: str
    init: dict = {}
    form: dict = {}
    pro:bool = False

    @field_validator("package")
    @classmethod
    def package_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Destination package cannot be empty")
        return value

    def encode(self):
        return b64_encoder(self)

    @staticmethod
    def decode(encoded_string) -> "DestinationConfig":
        return DestinationConfig(
            **b64_decoder(encoded_string)
        )


class Destination(NamedEntityInContext):
    description: Optional[str] = ""
    destination: DestinationConfig
    enabled: bool = False
    tags: List[str] = []
    mapping: dict = {}
    condition: Optional[str] = ""
    on_profile_change_only: Optional[bool] = True
    resource: Entity
    event_type: Optional[NamedEntity] = None
    source: NamedEntity
    locked: Optional[bool] = False

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("condition")
    @classmethod
    def is_valid_condition(cls, value):
        if value:
            _condition = Condition()
            try:
                _condition.parse(value)
            except Exception as e:
                raise ValueError("There is an error in the prerequisites field. The condition is incorrect. The system "
                                 "could not parse it. Please see the documentation for the condition syntax.", str(e))

        return value

    def _get_class_and_module(self):
        parts = self.destination.package.split(".")
        if len(parts) < 2:
            raise ValueError(f"Can not find class in package on {self.destination.package}")
        return ".".join(parts[:-1]), parts[-1]

    def get_destination_class(self) -> Callable:
        module, class_name = self._get_class_and_module()
        module = import_package(module)
        return load_callable(module, class_name)



