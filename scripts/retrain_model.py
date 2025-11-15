"""
Retrain KNN model with current scikit-learn version
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
import joblib
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

print("=" * 60)
print("Retraining KNN Model with Current scikit-learn Version")
print("=" * 60)

# 1. Load data
print("\n1. Loading data...")
formula_df = pd.read_csv("data/raw/formula_master.csv")
log_df = pd.read_csv("data/raw/feeding_logs.csv")

print(f"   Formulas: {len(formula_df)}")
print(f"   Feeding logs: {len(log_df)}")

# 2. Merge data
print("\n2. Merging data...")
data = log_df.merge(formula_df, on="formula_id", how="left")
print(f"   Total samples: {len(data)}")

# 3. Define features
baby_feature_cols = [
    "age_month",
    "sex",
    "height_cm",
    "weight_kg",
    "allergy_risk",
    "lactose_sensitivity",
    "feed_ml_per_intake",
]

formula_feature_cols = [
    "formula_id",
    "category",
    "lactose_level",
    "target_issue",
    "protein_type",
]

feature_cols = baby_feature_cols + formula_feature_cols
target_col = "overall_tolerance"

X = data[feature_cols].copy()
y = data[target_col].copy()

print(f"\n3. Features: {len(feature_cols)}")
print(f"   Target distribution:")
print(y.value_counts())

# 4. Encode target
print("\n4. Encoding target variable...")
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print(f"   Classes: {label_encoder.classes_}")

# 5. Define preprocessing
numeric_features = [
    "age_month",
    "height_cm",
    "weight_kg",
    "allergy_risk",
    "lactose_sensitivity",
    "feed_ml_per_intake",
]

categorical_features = [
    "sex",
    "formula_id",
    "category",
    "lactose_level",
    "target_issue",
    "protein_type",
]

print("\n5. Creating preprocessing pipeline...")
# 전처리 파이프라인 정의
numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])
categorical_transformer = Pipeline(steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

# 6. Create model pipeline
# KNN 모델 생성
print("\n6. Creating KNN model...")
knn_clf = KNeighborsClassifier(n_neighbors=5, weights="distance")

clf = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", knn_clf),
    ]
)

# 7. Train/test split
print("\n7. Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

# 8. Train model
print("\n8. Training model...")
clf.fit(X_train, y_train)
print("   ✅ Training complete")

# 9. Evaluate
print("\n9. Evaluating model...")
y_pred = clf.predict(X_test)
labels = list(range(len(label_encoder.classes_)))
print("\n" + "=" * 60)
print("Classification Report")
print("=" * 60)
print(
    classification_report(
        y_test, y_pred, labels=labels, target_names=label_encoder.classes_
    )
)

# 10. Save model
print("\n10. Saving model...")
model_package = {
    "model_pipeline": clf,
    "label_encoder": label_encoder,
    "feature_cols": feature_cols,
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "target_col": target_col,
}

output_path = "models/trained/knn_v1_retrained.pkl"
joblib.dump(model_package, output_path)
print(f"   ✅ Model saved to: {output_path}")

# 11. Test prediction
print("\n11. Testing prediction...")
test_profile = {
    "age_month": 4,
    "sex": "M",
    "height_cm": 62.0,
    "weight_kg": 6.5,
    "allergy_risk": 0,
    "lactose_sensitivity": 1,
    "feed_ml_per_intake": 90,
}

# Test with first formula
test_formula = formula_df.iloc[0]
test_case = {**test_profile}
test_case.update({
    "formula_id": int(test_formula["formula_id"]),
    "category": test_formula["category"],
    "lactose_level": test_formula["lactose_level"],
    "target_issue": test_formula["target_issue"],
    "protein_type": test_formula["protein_type"],
})

X_new = pd.DataFrame([test_case])[feature_cols]
y_pred_encoded = clf.predict(X_new)[0]
y_pred_label = label_encoder.inverse_transform([y_pred_encoded])[0]

print(f"   Test prediction: {y_pred_label}")

print("\n" + "=" * 60)
print("✅ Model retraining complete!")
print("=" * 60)
print(f"\nNext steps:")
print(f"1. Update api/services/recommender.py to use: {output_path}")
print(f"2. Or rename: mv {output_path} models/trained/knn_v1_legacy.pkl")
print(f"3. Restart API server")
