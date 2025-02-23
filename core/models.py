from datetime import datetime, date
from typing import Dict, Optional
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class DataBaseModel(BaseModel):
    def model_dump_csv(self) -> Dict[str, str]:
        dump = self.model_dump(mode="python")
        return {
            key: str(getattr(self, key)) if hasattr(self, key) else str(value)
            for key, value in dump.items()
        }


class Delay(DataBaseModel):
    years: Optional[int] = Field(..., title="Année", description="Nombre d'années")
    months: Optional[int] = Field(..., title="Mois", description="Nombre de mois")

    @field_validator("months")
    def validate_mois(cls, v: int, info: ValidationInfo) -> int:
        if v >= 12 or v < 0:
            raise ValueError("Le nombre de mois doit être compris entre 0 et 11")
        return v

    @field_validator("years")
    def validate_année(cls, v: int, info: ValidationInfo) -> int:
        if v < 0:
            raise ValueError("Le nombre d'années doit être positif")
        return v

    def __str__(self) -> str:
        parts = []
        if self.years:
            parts.append(f"{self.years} an{'s' if self.years > 1 else ''}")
        if self.months:
            parts.append(f"{self.months} mois")
        return " et ".join(parts) if parts else "0 mois"


class Date(DataBaseModel):
    day: int = Field(..., description="Jour du mois")
    month: int = Field(..., description="Mois de l'année")
    year: int = Field(..., description="Année")

    @field_validator("month")
    def validate_month(cls, v: int, info: ValidationInfo) -> int:
        if v > 12 or v < 1:
            raise ValueError("Le mois doit être compris entre 1 et 12")
        return v

    @field_validator("day")
    def validate_day(cls, v: int, info: ValidationInfo) -> int:
        if v > 31 or v < 1:
            raise ValueError("Le jour doit être compris entre 1 et 31")
        return v

    def is_before(self, other: "Date") -> bool:
        if self.year < other.year:
            return True
        if self.year == other.year:
            if self.month < other.month:
                return True
            if self.month == other.month:
                return self.day < other.day
        return False

    def is_after(self, other: "Date") -> bool:
        return not self.is_before(other)

    def diff(self, other: "Date") -> relativedelta:
        return relativedelta(
            datetime(other.year, other.month, other.day) + relativedelta(days=1),
            datetime(self.year, self.month, self.day),
        )

    def __str__(self) -> str:
        return f"{self.day:02d}/{self.month:02d}/{self.year}"
