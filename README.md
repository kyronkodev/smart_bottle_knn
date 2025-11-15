# Smart Bottle Formula Recommender

AI-powered baby formula recommendation system integrated with Smart Bottle IoT ecosystem.

## 📋 Overview

This project provides machine learning-based formula recommendations for babies based on their profile, feeding patterns, and health indicators. It integrates with the Smart Bottle hardware system to leverage real-time feeding data.

## 🎯 Features

- **Formula Recommendation API**: RESTful API for personalized formula recommendations
- **Tolerance Prediction**: Predict baby's tolerance (good/moderate/poor) for specific formulas
- **Smart Bottle Integration**: Connects to Smart Bottle MySQL database for real-time data
- **Multiple Models**: Support for K-NN, Random Forest, XGBoost, and ensemble models
- **Probability-Based Ranking**: Recommendations ranked by predicted "good" tolerance probability

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Smart Bottle IoT Ecosystem          │
├─────────────────────────────────────────┤
│  [ESP32] → [Node.js] → [MySQL]         │
│   Sensors    Server      Database       │
│                             ↓           │
│                    smartbottle_model    │
│                    Python ML Service    │
│                             ↓           │
│                      FastAPI Server     │
│                             ↓           │
│                    Formula Recommender  │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
cd /Users/kkj/Desktop/Develop/kkj/smartbottle_model

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
# DB_HOST=211.192.7.222
# DB_PORT=3306
# DB_USER=your_username
# DB_PASSWORD=your_password
# DB_NAME=smart_bottle
```

### 3. Run API Server

```bash
# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python api/main.py
```

### 4. Access API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### POST /api/v1/recommend

Get formula recommendations for a baby profile.

**Request:**
```json
{
  "age_month": 4,
  "sex": "M",
  "height_cm": 62.0,
  "weight_kg": 6.5,
  "allergy_risk": 0,
  "lactose_sensitivity": 1,
  "feed_ml_per_intake": 90
}
```

**Response:**
```json
{
  "status": "success",
  "baby_profile": {...},
  "recommendations": [
    {
      "formula_id": 4,
      "formula_brand": "GutCare_Constipation",
      "category": "constipation_care",
      "good_probability": 0.848,
      "predicted_tolerance": "good"
    }
  ],
  "model_version": "knn_v1_legacy"
}
```

### POST /api/v1/predict

Predict tolerance for specific baby-formula combination.

**Request:**
```json
{
  "baby_profile": {...},
  "formula_id": 3
}
```

### GET /api/v1/formulas

List all available formulas.

### GET /api/v1/formulas/{formula_id}

Get details for a specific formula.

## 📊 Available Formulas

| ID | Brand | Category | Target Issue |
|----|-------|----------|--------------|
| 1 | MilkySoft_Normal | normal | none |
| 2 | MilkySoft_Sensitive | sensitive | sensitive |
| 3 | LactoFree | low_lactose | lactose_intolerance |
| 4 | GutCare_Constipation | constipation_care | constipation |
| 5 | GentlePlus | gentle | digestion |
| 6 | PremiumHA | allergy_care | allergy |

## 🧪 Testing

### Test Data Loader

```bash
python src/data/data_loader.py
```

### Test Recommender Service

```bash
python api/services/recommender.py
```

### Test API with curl

```bash
# Recommend formulas
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "age_month": 4,
    "sex": "M",
    "height_cm": 62.0,
    "weight_kg": 6.5,
    "allergy_risk": 0,
    "lactose_sensitivity": 1,
    "feed_ml_per_intake": 90
  }'

# List formulas
curl http://localhost:8000/api/v1/formulas
```

## 🔗 Node.js Integration

### Add to Smart Bottle Server

```javascript
// smart_bottle/app/services/ml_service.js
const axios = require('axios');

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';

async function getFormulaRecommendation(babyProfile) {
    const response = await axios.post(
        `${ML_API_URL}/api/v1/recommend`,
        babyProfile
    );
    return response.data;
}

module.exports = { getFormulaRecommendation };
```

### Use in Controller

```javascript
const mlService = require('../services/ml_service');

async function recommendFormula(req, res) {
    const babyProfile = {
        age_month: 4,
        sex: 'M',
        height_cm: 62.0,
        weight_kg: 6.5,
        allergy_risk: 0,
        lactose_sensitivity: 1,
        feed_ml_per_intake: 90
    };

    const recommendations = await mlService.getFormulaRecommendation(babyProfile);
    res.json(recommendations);
}
```

## 📁 Project Structure

```
smartbottle_model/
├── api/                      # FastAPI application
│   ├── main.py              # Main app entry point
│   ├── routers/             # API route handlers
│   ├── schemas/             # Pydantic models
│   └── services/            # Business logic
├── config/                  # Configuration
│   └── database.py          # DB connection
├── data/                    # Data files
│   ├── raw/                 # Original CSV data
│   ├── processed/           # Processed data
│   └── features/            # Generated features
├── models/                  # ML models
│   └── trained/             # Saved models
├── src/                     # Source code
│   ├── data/                # Data loading
│   ├── training/            # Model training
│   ├── evaluation/          # Model evaluation
│   └── utils/               # Utilities
├── notebooks/               # Jupyter notebooks
├── tests/                   # Unit tests
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Development

### Add New Model

1. Train model and save to `models/trained/`
2. Update `api/services/recommender.py` to load new model
3. Test with `python api/services/recommender.py`

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📈 Model Performance

Current model (K-NN v1):
- **Good class**: Precision 0.69, Recall 0.73
- **Moderate class**: Precision 0.00 (needs improvement)
- **Poor class**: Precision 0.00 (needs improvement)

See `MODEL_PROPOSAL.md` for improvement roadmap.

## 🗺️ Roadmap

### Phase 1 (Completed ✅)
- [x] Project structure
- [x] Legacy model migration
- [x] FastAPI server
- [x] Recommendation API
- [x] Database integration

### Phase 2 (In Progress 🔄)
- [ ] Improve model performance (SMOTE, ensemble)
- [ ] Add time-series features
- [ ] Symptom-based recommendations
- [ ] Model explainability (SHAP/LIME)

### Phase 3 (Planned 📋)
- [ ] Collaborative filtering
- [ ] Growth prediction
- [ ] Anomaly detection
- [ ] Production deployment

## 📚 Documentation

- **Project Overview**: `PROJECT_OVERVIEW.md` - Complete system documentation
- **Model Proposal**: `MODEL_PROPOSAL.md` - Detailed improvement plan
- **API Reference**: http://localhost:8000/docs (when server running)

## 🔧 Troubleshooting

### Model Not Loading
```bash
# Check model file exists
ls -lh models/trained/knn_v1_legacy.pkl

# Check data files exist
ls -lh data/raw/
```

### Database Connection Failed
```bash
# Test database connection
python config/database.py

# Check .env file
cat .env
```

### API Server Won't Start
```bash
# Check port availability
lsof -i :8000

# Check dependencies
pip list | grep fastapi
```

## 🤝 Contributing

This is a university project for IoT Service Big Data Analysis course.

## 📄 License

Educational project - Yonsei University

## 📞 Support

For questions or issues:
- Check `PROJECT_OVERVIEW.md`
- Check `MODEL_PROPOSAL.md`
- Review API documentation at `/docs`

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0
**Python**: 3.10+
**Status**: Development
