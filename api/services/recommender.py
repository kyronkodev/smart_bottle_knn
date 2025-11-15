"""
Formula recommendation service
"""
import joblib
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


class FormulaRecommender:
    """Formula recommendation engine"""

    def __init__(self, model_path: str = "models/trained/knn_v1_legacy.pkl"):
        """
        Initialize recommender with trained model

        Args:
            model_path: Path to trained model pickle file
        """
        self.model_path = Path(model_path)
        self.model_package = None
        self.model = None
        self.label_encoder = None
        self.feature_cols = None
        self.formula_df = None
        self.model_version = "unknown"

        self.load_model()
        self.load_formula_data()

    def load_model(self):
        """Load trained model from pickle file"""
        try:
            self.model_package = joblib.load(self.model_path)
            self.model = self.model_package["model_pipeline"]
            self.label_encoder = self.model_package["label_encoder"]
            self.feature_cols = self.model_package["feature_cols"]
            self.model_version = self.model_path.stem

            logger.info(f"Model loaded successfully: {self.model_version}")
            logger.info(f"Features: {self.feature_cols}")
            logger.info(f"Classes: {self.label_encoder.classes_}")

        except FileNotFoundError:
            logger.error(f"Model file not found: {self.model_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def load_formula_data(self):
        """Load formula master data"""
        try:
            formula_path = Path("data/raw/formula_master.csv")
            self.formula_df = pd.read_csv(formula_path)
            logger.info(f"Loaded {len(self.formula_df)} formulas")

        except FileNotFoundError:
            logger.error("Formula master data not found")
            raise
        except Exception as e:
            logger.error(f"Error loading formula data: {e}")
            raise

    def recommend(
        self,
        baby_profile: Dict,
        top_n: int = 3,
        min_good_prob: float = 0.3
    ) -> List[Dict]:
        """
        Recommend formulas for a baby

        Args:
            baby_profile: Dictionary with baby profile data
            top_n: Number of top recommendations to return
            min_good_prob: Minimum good probability threshold

        Returns:
            List of recommendation dictionaries
        """
        try:
            # Find 'good' class index
            classes = self.label_encoder.classes_
            try:
                good_index = list(classes).index("good")
            except ValueError:
                raise ValueError(f"'good' class not found in: {classes}")

            # 1. 아기 프로필과 6가지 분유 조합 생성
            candidates = []
            for _, formula in self.formula_df.iterrows():
                candidate = {**baby_profile}
                candidate.update({
                    "formula_id": int(formula["formula_id"]),
                    "category": formula["category"],
                    "lactose_level": formula["lactose_level"],
                    "target_issue": formula["target_issue"],
                    "protein_type": formula["protein_type"],
                })
                candidates.append(candidate)

            candidates_df = pd.DataFrame(candidates)
            X_candidates = candidates_df[self.feature_cols]

           # 2. KNN 모델로 예측
            prob_matrix = self.model.predict_proba(X_candidates)
            good_probs = prob_matrix[:, good_index]

            # Predict classes
            y_pred_encoded = self.model.predict(X_candidates)
            y_pred_labels = self.label_encoder.inverse_transform(y_pred_encoded)

            # Build results
            recommendations = []
            for i, (_, formula) in enumerate(self.formula_df.iterrows()):
                rec = {
                    "formula_id": int(formula["formula_id"]),
                    "formula_brand": formula["formula_brand"],
                    "category": formula["category"],
                    "lactose_level": formula["lactose_level"],
                    "target_issue": formula["target_issue"],
                    "protein_type": formula["protein_type"],
                    "good_probability": float(good_probs[i]),
                    "predicted_tolerance": y_pred_labels[i],
                }
                recommendations.append(rec)

            # 3. 확률 순 정렬 및 Top N 반환
            recommendations.sort(key=lambda x: x["good_probability"], reverse=True)

            # Filter by minimum probability
            filtered = [r for r in recommendations if r["good_probability"] >= min_good_prob]

            # Return top N
            top_recommendations = filtered[:top_n]

            logger.info(f"Generated {len(top_recommendations)} recommendations (from {len(filtered)} filtered)")

            return {
                "recommendations": top_recommendations,
                "all_formulas": recommendations
            }

        except Exception as e:
            logger.error(f"Error in recommendation: {e}")
            raise

    def predict_single(
        self,
        baby_profile: Dict,
        formula_id: int
    ) -> Dict:
        """
        Predict tolerance for a specific baby-formula combination

        Args:
            baby_profile: Dictionary with baby profile
            formula_id: Formula identifier

        Returns:
            Prediction dictionary
        """
        try:
            # Get formula info
            formula = self.formula_df[self.formula_df["formula_id"] == formula_id]
            if len(formula) == 0:
                raise ValueError(f"Formula ID {formula_id} not found")

            formula = formula.iloc[0]

            # Create test case
            test_case = {**baby_profile}
            test_case.update({
                "formula_id": int(formula["formula_id"]),
                "category": formula["category"],
                "lactose_level": formula["lactose_level"],
                "target_issue": formula["target_issue"],
                "protein_type": formula["protein_type"],
            })

            X_test = pd.DataFrame([test_case])[self.feature_cols]

            # Predict
            y_pred_encoded = self.model.predict(X_test)[0]
            y_pred_label = self.label_encoder.inverse_transform([y_pred_encoded])[0]

            # Get probabilities
            prob_matrix = self.model.predict_proba(X_test)
            classes = self.label_encoder.classes_
            good_index = list(classes).index("good")
            good_prob = float(prob_matrix[0, good_index])

            result = {
                "formula_id": formula_id,
                "formula_brand": formula["formula_brand"],
                "predicted_tolerance": y_pred_label,
                "good_probability": good_prob,
                "probabilities": {
                    class_name: float(prob_matrix[0, i])
                    for i, class_name in enumerate(classes)
                }
            }

            logger.info(f"Prediction for formula {formula_id}: {y_pred_label} ({good_prob:.3f})")

            return result

        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise


if __name__ == "__main__":
    # Test recommender
    logging.basicConfig(level=logging.INFO)

    recommender = FormulaRecommender()

    test_profile = {
        "age_month": 4,
        "sex": "M",
        "height_cm": 62.0,
        "weight_kg": 6.5,
        "allergy_risk": 0,
        "lactose_sensitivity": 1,
        "feed_ml_per_intake": 90,
    }

    print("\n=== Testing Recommendation ===")
    result = recommender.recommend(test_profile, top_n=3)

    print("\nTop 3 Recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"{i}. {rec['formula_brand']} - {rec['good_probability']:.3f}")

    print("\n=== Testing Single Prediction ===")
    pred = recommender.predict_single(test_profile, formula_id=3)
    print(f"Formula: {pred['formula_brand']}")
    print(f"Predicted: {pred['predicted_tolerance']}")
    print(f"Good prob: {pred['good_probability']:.3f}")
