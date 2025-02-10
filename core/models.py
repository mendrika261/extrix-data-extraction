from datetime import datetime
from typing import Optional
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class Delay(BaseModel):
    years: Optional[int] = Field(default=0, title="Année", description="Nombre d'années")
    months: Optional[int] = Field(default=0, title="Mois", description="Nombre de mois")
    
    @field_validator('months')
    def validate_mois(cls, v: int, info: ValidationInfo) -> int:
        if v >= 12 or v < 0:
            raise ValueError('Le nombre de mois doit être compris entre 0 et 11')
        return v
    
    @field_validator('years')
    def validate_année(cls, v: int, info: ValidationInfo) -> int:
        if v < 0:
            raise ValueError('Le nombre d\'années doit être positif')
        return v


class Leasing(BaseModel):
    bailleur: str = Field(
        ..., 
        title="Bailleur",
        description="Nom de la société UNIQUEMENT ou prénom nom de la personne UNIQUEMENT"
    )
    preneur: str = Field(
        ..., 
        title="Preneur",
        description="Nom de la société UNIQUEMENT ou prénom nom de la personne UNIQUEMENT"
    )
    adresse: str = Field(
        ..., 
        title="Adresse du bien loué",
        description="Numéro, rue, code postal, ville"
    )
    description: str = Field(
        ..., 
        title="Description du bien",
        description="Description sous forme de liste, avec usages et équipements inclus, pas de phrases"
    )
    surface: float = Field(
        ..., 
        title="Surface",
        description="Surface du bien loué en m²"
    )
    date_prise_effet: datetime = Field(
        ..., 
        title="Date de prise d'effet",
        description="Date de prise d'effet du bail"
    )
    date_fin: datetime = Field(
        ..., 
        title="Date de fin",
        description="Date de fin du bail"
    )
    duree_bail: Delay = Field(
        ..., 
        title="Durée du bail",
        description="Durée du bail en années et mois"
    )

    @field_validator('date_fin')
    def validate_date_fin(cls, v: datetime, info: ValidationInfo) -> datetime:
        date_prise_effet = info.data.get('date_prise_effet')
        if date_prise_effet and v > date_prise_effet:
            raise ValueError('La date de fin doit être après la date de prise d\'effet')
        return v
    
    @field_validator('duree_bail')
    def validate_duree_bail(cls, v: Delay, info: ValidationInfo) -> Delay:
        date_prise_effet = info.data.get('date_prise_effet')
        date_fin = info.data.get('date_fin')
        if date_prise_effet and date_fin:
            diff = relativedelta(date_fin + relativedelta(months=1), date_prise_effet)
            if diff != v:
                raise ValueError(f'La durée du bail doit être de {diff} au lieu de {v}')
        return v

    model_config = {
        "json_schema_extra": {
            "description": "Informations extraites d'un contrat de location"
        }
    }
