"""
Pydantic schemas for baby profiles
"""
from pydantic import BaseModel, Field
from typing import Optional


class BabyProfile(BaseModel):
    """Baby profile for formula recommendation"""

    age_month: int = Field(..., ge=0, le=36, description="Age in months (0-36)")
    sex: str = Field(..., pattern="^[MF]$", description="Sex: M or F")
    height_cm: float = Field(..., gt=0, le=150, description="Height in centimeters")
    weight_kg: float = Field(..., gt=0, le=50, description="Weight in kilograms")
    allergy_risk: int = Field(..., ge=0, le=1, description="Allergy risk: 0 or 1")
    lactose_sensitivity: int = Field(..., ge=0, le=1, description="Lactose sensitivity: 0 or 1")
    feed_ml_per_intake: int = Field(..., gt=0, le=300, description="Feeding amount per intake in ml")

    class Config:
        schema_extra = {
            "example": {
                "age_month": 4,
                "sex": "M",
                "height_cm": 62.0,
                "weight_kg": 6.5,
                "allergy_risk": 0,
                "lactose_sensitivity": 1,
                "feed_ml_per_intake": 90
            }
        }


class BabyProfileWithSymptoms(BabyProfile):
    """Baby profile with recent symptoms"""

    diarrhea: Optional[int] = Field(0, ge=0, le=1, description="Diarrhea: 0 or 1")
    constipation: Optional[int] = Field(0, ge=0, le=1, description="Constipation: 0 or 1")
    vomiting: Optional[int] = Field(0, ge=0, le=1, description="Vomiting: 0 or 1")
    skin_rash: Optional[int] = Field(0, ge=0, le=1, description="Skin rash: 0 or 1")

    class Config:
        schema_extra = {
            "example": {
                "age_month": 4,
                "sex": "M",
                "height_cm": 62.0,
                "weight_kg": 6.5,
                "allergy_risk": 0,
                "lactose_sensitivity": 1,
                "feed_ml_per_intake": 90,
                "diarrhea": 0,
                "constipation": 1,
                "vomiting": 0,
                "skin_rash": 0
            }
        }
