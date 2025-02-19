from typing import Any, Callable, Dict
from dateutil.relativedelta import relativedelta
from pydantic import ValidationInfo
from pydantic_core import PydanticCustomError

from core.models import Date, Delay


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
def validate_date_after(v: Date, info: ValidationInfo, *, field: str) -> Date:
    other_date = info.data.get(field)
    if other_date and v.is_before(other_date):
        raise PydanticCustomError(
            "date_after", "La date doit être après {field}", {"field": field}
        )
    return v


@ValidatorRegistry.register("date_before")
def validate_date_before(v: Date, info: ValidationInfo, *, field: str) -> Date:
    other_date = info.data.get(field)
    if other_date and v.is_after(other_date):
        raise PydanticCustomError(
            "date_before", "La date doit être avant {field}", {"field": field}
        )
    return v


@ValidatorRegistry.register("delay_matches_dates")
def validate_delay_matches_dates(
    v: Delay, info: ValidationInfo, *, start_date: str, end_date: str
) -> Delay:
    date_start = info.data.get(start_date)
    date_end = info.data.get(end_date)

    if date_start and date_end:
        diff = date_start.diff(date_end)
        if v.years != diff.years or v.months != diff.months:
            raise PydanticCustomError(
                "delay_matches_dates",
                "La durée du bail doit être de {diff} au lieu de {v}",
                {"diff": diff, "v": v},
            )
    return v
