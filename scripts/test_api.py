"""
Quick test script for Smart Bottle Formula Recommender API
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_list_formulas():
    """Test formula listing"""
    print("\n=== Testing Formula List ===")
    response = requests.get(f"{API_URL}/api/v1/formulas")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total formulas: {data['count']}")
    for formula in data['formulas']:
        print(f"  - {formula['formula_id']}: {formula['formula_brand']}")
    return response.status_code == 200

def test_recommendation():
    """Test recommendation endpoint"""
    print("\n=== Testing Recommendation ===")

    baby_profile = {
        "age_month": 4,
        "sex": "M",
        "height_cm": 62.0,
        "weight_kg": 6.5,
        "allergy_risk": 0,
        "lactose_sensitivity": 1,
        "feed_ml_per_intake": 90
    }

    response = requests.post(
        f"{API_URL}/api/v1/recommend",
        json=baby_profile
    )

    print(f"Status: {response.status_code}")
    data = response.json()

    print(f"\nBaby Profile:")
    print(f"  Age: {baby_profile['age_month']} months")
    print(f"  Sex: {baby_profile['sex']}")
    print(f"  Weight: {baby_profile['weight_kg']} kg")

    print(f"\nTop Recommendations:")
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"\n{i}. {rec['formula_brand']}")
        print(f"   Category: {rec['category']}")
        print(f"   Target: {rec['target_issue']}")
        print(f"   Good Probability: {rec['good_probability']:.1%}")
        print(f"   Predicted: {rec['predicted_tolerance']}")

    return response.status_code == 200

def test_prediction():
    """Test single prediction endpoint"""
    print("\n=== Testing Single Prediction ===")

    baby_profile = {
        "age_month": 4,
        "sex": "M",
        "height_cm": 62.0,
        "weight_kg": 6.5,
        "allergy_risk": 0,
        "lactose_sensitivity": 1,
        "feed_ml_per_intake": 90
    }

    formula_id = 3  # LactoFree

    response = requests.post(
        f"{API_URL}/api/v1/predict",
        json=baby_profile,
        params={"formula_id": formula_id}
    )

    print(f"Status: {response.status_code}")
    data = response.json()

    pred = data['prediction']
    print(f"\nFormula: {pred['formula_brand']}")
    print(f"Predicted Tolerance: {pred['predicted_tolerance']}")
    print(f"Good Probability: {pred['good_probability']:.1%}")
    print(f"\nAll Probabilities:")
    for class_name, prob in pred['probabilities'].items():
        print(f"  {class_name}: {prob:.1%}")

    return response.status_code == 200

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Smart Bottle Formula Recommender API Tests")
    print("=" * 60)

    tests = [
        ("Health Check", test_health),
        ("List Formulas", test_list_formulas),
        ("Recommendation", test_recommendation),
        ("Single Prediction", test_prediction),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASS" if success else "❌ FAIL"))
        except Exception as e:
            print(f"\nError in {test_name}: {e}")
            results.append((test_name, f"❌ ERROR: {e}"))

    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    for test_name, result in results:
        print(f"{test_name}: {result}")

if __name__ == "__main__":
    run_all_tests()
