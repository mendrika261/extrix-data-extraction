from typing import Any, Callable, Dict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pydantic import ValidationInfo

from core.models import Delay

class ValidatorRegistry:
    _validators: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls._validators[name] = func
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        if name not in cls._validators:
            raise ValueError(f"Validator {name} not found")
        return cls._validators[name]

@ValidatorRegistry.register("date_after")
def validate_date_after(v: datetime, info: ValidationInfo, *, field: str) -> datetime:
    other_date = info.data.get(field)
    if other_date and v < other_date:
        raise ValueError(f'La date doit être après {field}')
    return v

@ValidatorRegistry.register("date_before")
def validate_date_before(v: datetime, info: ValidationInfo, *, field: str) -> datetime:
    other_date = info.data.get(field)
    if other_date and v > other_date:
        raise ValueError(f'La date doit être avant {field}')
    return v

@ValidatorRegistry.register("delay_matches_dates")
def validate_delay_matches_dates(v: Delay, info: ValidationInfo, *, start_date: str, end_date: str) -> Delay:
    date_start = info.data.get(start_date)
    date_end = info.data.get(end_date)

    if date_start and date_end:
        diff = relativedelta(date_end + relativedelta(months=1), date_start)
        if diff != v:
            raise ValueError(f'La durée du bail doit être de {diff} au lieu de {v}')
    return v
