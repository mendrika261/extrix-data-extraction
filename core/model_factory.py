from pathlib import Path
from typing import List, Optional, Type, Any, Dict, Callable
from pydantic import BaseModel, create_model, Field, field_validator
from datetime import datetime

from core.models import DataBaseModel, Date, Delay
from core.utils import load_json_file, write_json, write_csv
from core.validators import ValidatorRegistry

class FieldJson(BaseModel):
    field_type: str = Field(...)
    title: str = Field(...)
    description: Optional[str] = None
    required: bool = True
    default: Any = None
    validators: List[Dict[str, Any]] = Field(default_factory=list)


class ModelJson(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    fields: Dict[str, FieldJson] = Field(...)


class ModelFactory:
    TYPE_MAPPING = {
        'str': str,
        'int': int,
        'float': float,
        'datetime': datetime,
        'bool': bool,
        'date': Date,
        'delay': Delay
    }

    @classmethod
    def _create_field_definition(cls, field_config: FieldJson) -> tuple[Type, Any]:
        field_type = cls.TYPE_MAPPING.get(field_config.field_type)
        if not field_type:
            raise ValueError(f"Unsupported field type: {field_config.field_type}")
        
        default = ... if field_config.required else field_config.default
        return (field_type, Field(
            default=default,
            title=field_config.title,
            description=field_config.description
        ))

    @classmethod
    def _create_validators(cls, fields_config: Dict[str, FieldJson]) -> Dict[str, Callable]:
        validators = {}
        
        for field_name, field_config in fields_config.items():
            for validator_config in field_config.validators:
                if validator_config['type'] == 'registered':
                    base_validator = ValidatorRegistry.get(validator_config['name'])
                    params = validator_config.get('params', {})
                    
                    def create_validator(base_func, fixed_params):
                        def wrapper(cls, v, info):
                            return base_func(v, info, **fixed_params)
                        return wrapper
                    
                    validator_name = f"validate_{field_name}"
                    validators[validator_name] = field_validator(field_name)(
                        create_validator(base_validator, params)
                    )
        
        return validators

    @classmethod
    def create_model(cls, config: ModelJson) -> Type[BaseModel]:
        fields = {
            name: cls._create_field_definition(field_config)
            for name, field_config in config.fields.items()
        }
        validators = cls._create_validators(config.fields)
        
        model = create_model(
            config.name,
            __module__=__name__,
            __base__=(DataBaseModel),
            __validators__=validators,
            **fields
        )
        
        model.model_config = {
            "json_schema_extra": {
                "description": config.description
            }
        }
        
        return model

    @staticmethod
    def load_model_json_file(file_path: str) -> ModelJson:
        return ModelJson.model_validate(load_json_file(file_path))

    @staticmethod
    def write_output(model: BaseModel, output_path: str) -> None:
        path = Path(output_path)
        format_extension = path.suffix.lower()[1:]
        
        if format_extension not in ['json', 'csv']:
            raise ValueError(f"Unsupported output format: {format_extension}")

        if format_extension == 'json':
            write_json(path, model.model_dump())
        else:  # csv
            write_csv(path, model.model_dump_csv())