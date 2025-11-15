"""
Pydantic schemas for formulas
"""
from pydantic import BaseModel
from typing import Optional


class Formula(BaseModel):
    """Formula product information"""

    formula_id: int
    formula_brand: str
    category: str
    lactose_level: str
    target_issue: str
    protein_type: str

    class Config:
        schema_extra = {
            "example": {
                "formula_id": 1,
                "formula_brand": "MilkySoft_Normal",
                "category": "normal",
                "lactose_level": "normal",
                "target_issue": "none",
                "protein_type": "standard"
            }
        }


class FormulaRecommendation(BaseModel):
    """Formula recommendation with probability"""

    formula_id: int
    formula_brand: str
    category: str
    lactose_level: str
    target_issue: str
    protein_type: str
    good_probability: float
    predicted_tolerance: Optional[str] = None
    recommendation_reason: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "formula_id": 4,
                "formula_brand": "GutCare_Constipation",
                "category": "constipation_care",
                "lactose_level": "normal",
                "target_issue": "constipation",
                "protein_type": "standard",
                "good_probability": 0.848,
                "predicted_tolerance": "good",
                "recommendation_reason": "Optimized for constipation issues"
            }
        }
