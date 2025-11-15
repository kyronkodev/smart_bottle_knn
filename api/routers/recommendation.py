"""
Formula recommendation API router
"""
from fastapi import APIRouter, HTTPException
from typing import List
import logging

from ..schemas.baby import BabyProfile
from ..schemas.formula import FormulaRecommendation
from ..schemas.recommendation import RecommendationResponse
from ..services.recommender import FormulaRecommender

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["recommendation"])

# Initialize recommender (singleton)
recommender = None


def get_recommender():
    """Get or create recommender instance"""
    global recommender
    if recommender is None:
        recommender = FormulaRecommender()
    return recommender


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_formula(
    baby_profile: BabyProfile,
    top_n: int = 3,
    min_good_prob: float = 0.3
):
    """
    Recommend formulas for a baby profile

    Args:
        baby_profile: Baby profile information
        top_n: Number of top recommendations (default: 3)
        min_good_prob: Minimum good probability threshold (default: 0.3)

    Returns:
        Recommendation response with top N formulas
    """
    try:
        rec_engine = get_recommender()

        # Convert Pydantic model to dict
        baby_dict = baby_profile.dict()

        # Get recommendations
        result = rec_engine.recommend(
            baby_profile=baby_dict,
            top_n=top_n,
            min_good_prob=min_good_prob
        )

        # Build response
        response = {
            "status": "success",
            "baby_profile": baby_dict,
            "recommendations": result["recommendations"],
            "all_formulas": result["all_formulas"],
            "model_version": rec_engine.model_version
        }

        logger.info(f"Recommendation generated for baby: age={baby_dict['age_month']}m, sex={baby_dict['sex']}")

        return response

    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def predict_tolerance(
    baby_profile: BabyProfile,
    formula_id: int
):
    """
    Predict tolerance for a specific baby-formula combination

    Args:
        baby_profile: Baby profile information
        formula_id: Formula identifier

    Returns:
        Prediction with probabilities
    """
    try:
        rec_engine = get_recommender()

        baby_dict = baby_profile.dict()

        result = rec_engine.predict_single(
            baby_profile=baby_dict,
            formula_id=formula_id
        )

        logger.info(f"Prediction for formula {formula_id}: {result['predicted_tolerance']}")

        return {
            "status": "success",
            "baby_profile": baby_dict,
            "prediction": result,
            "model_version": rec_engine.model_version
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in prediction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formulas")
async def list_formulas():
    """
    Get list of all available formulas

    Returns:
        List of formula products
    """
    try:
        rec_engine = get_recommender()

        formulas = rec_engine.formula_df.to_dict('records')

        return {
            "status": "success",
            "count": len(formulas),
            "formulas": formulas
        }

    except Exception as e:
        logger.error(f"Error listing formulas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formulas/{formula_id}")
async def get_formula(formula_id: int):
    """
    Get specific formula details

    Args:
        formula_id: Formula identifier

    Returns:
        Formula details
    """
    try:
        rec_engine = get_recommender()

        formula = rec_engine.formula_df[rec_engine.formula_df["formula_id"] == formula_id]

        if len(formula) == 0:
            raise HTTPException(status_code=404, detail=f"Formula {formula_id} not found")

        return {
            "status": "success",
            "formula": formula.iloc[0].to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting formula: {e}")
        raise HTTPException(status_code=500, detail=str(e))
