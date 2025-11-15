"""
Pydantic schemas for recommendations
"""
from pydantic import BaseModel
from typing import List
from .baby import BabyProfile
from .formula import FormulaRecommendation


class RecommendationRequest(BaseModel):
    """Request for formula recommendation"""

    baby_profile: BabyProfile
    top_n: int = 3
    min_good_prob: float = 0.3

    class Config:
        schema_extra = {
            "example": {
                "baby_profile": {
                    "age_month": 4,
                    "sex": "M",
                    "height_cm": 62.0,
                    "weight_kg": 6.5,
                    "allergy_risk": 0,
                    "lactose_sensitivity": 1,
                    "feed_ml_per_intake": 90
                },
                "top_n": 3,
                "min_good_prob": 0.3
            }
        }


class RecommendationResponse(BaseModel):
    """Response with formula recommendations"""

    status: str
    baby_profile: dict
    recommendations: List[FormulaRecommendation]
    all_formulas: List[FormulaRecommendation]
    model_version: str

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "baby_profile": {
                    "age_month": 4,
                    "sex": "M",
                    "height_cm": 62.0,
                    "weight_kg": 6.5,
                    "allergy_risk": 0,
                    "lactose_sensitivity": 1,
                    "feed_ml_per_intake": 90
                },
                "recommendations": [
                    {
                        "formula_id": 4,
                        "formula_brand": "GutCare_Constipation",
                        "category": "constipation_care",
                        "lactose_level": "normal",
                        "target_issue": "constipation",
                        "protein_type": "standard",
                        "good_probability": 0.848,
                        "predicted_tolerance": "good"
                    }
                ],
                "all_formulas": [],
                "model_version": "knn_v1_legacy"
            }
        }
