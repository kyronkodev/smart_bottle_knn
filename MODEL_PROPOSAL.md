# Smart Bottle 분유 추천 모델 제안서

## 📊 현황 분석

### 제공된 자료 분석 결과

**프로젝트**: IoT서비스빅데이터 분석 - 분유추천 K-NN 모델
**위치**: `/Users/kkj/Desktop/연세대/3학기/IoT서비스빅데이터 분석 /final/분유추천`

#### 기존 구현 내용

**1. 데이터셋**
- `분유데이터.csv`: 6개 분유 제품 정보
- `수유데이터.csv`: 100건의 수유 로그 데이터

**2. 모델**
- 알고리즘: K-Nearest Neighbors (K=5, distance weighting)
- 입력 피처: 12개 (아기 7개 + 분유 5개)
- 타겟: overall_tolerance (good/moderate/poor)
- 성능: good 클래스만 예측 가능 (precision 0.69)

**3. 기능**
- 분유 내성 예측
- 확률 기반 분유 추천 (상위 N개)

---

## 🎯 Smart Bottle 시스템 통합 전략

### 시스템 연계 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                    Smart Bottle Ecosystem                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Arduino ESP32]  ←─Socket.IO─→  [Node.js Server]               │
│   - 온도 센서                        - MySQL DB                  │
│   - 무게 센서                        - 수유 기록                 │
│   - 실시간 데이터                    - 아기 프로필               │
│                                            ↓                     │
│                                     [데이터 수집]                │
│                                            ↓                     │
│                                  ┌─────────────────┐            │
│                                  │ smartbottle_model│            │
│                                  ├─────────────────┤            │
│                                  │ 1. 데이터 전처리  │            │
│                                  │ 2. 특징 추출     │            │
│                                  │ 3. 모델 학습     │            │
│                                  │ 4. 분유 추천     │            │
│                                  │ 5. 패턴 분석     │            │
│                                  └─────────────────┘            │
│                                            ↓                     │
│                                  [추천 API 서비스]               │
│                                            ↓                     │
│                                     [웹 대시보드]                │
│                                   - 분유 추천 표시               │
│                                   - 분석 리포트                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚨 문제점 및 개선 방향

### 기존 모델의 한계

#### 1. 데이터 품질 문제
```
문제점:
❌ 데이터 부족: 100건 (학습 80건, 검증 20건)
❌ 클래스 불균형: good 75%, moderate 20%, poor 5%
❌ 제한된 분유: 6개 제품만
❌ 시간 정보 없음: 수유 이력 추적 불가

개선안:
✅ Smart Bottle 실제 데이터 활용 → 수백~수천 건 확보
✅ SMOTE/오버샘플링으로 클래스 균형 조정
✅ 분유 DB 확장 (실제 시판 제품 추가)
✅ 시계열 데이터 추가 (feeding_sessions 테이블 활용)
```

#### 2. 모델 성능 문제
```
문제점:
❌ moderate/poor 클래스 예측 불가 (precision 0.00)
❌ K-NN만으로는 복잡한 패턴 학습 한계
❌ 피처 엔지니어링 부족

개선안:
✅ 앙상블 모델 적용 (Random Forest, XGBoost, LightGBM)
✅ 클래스 가중치 조정 (class_weight='balanced')
✅ 고급 피처 생성 (성장 속도, 수유 패턴 등)
```

#### 3. 실용성 문제
```
문제점:
❌ 실시간 추천 불가능 (배치 처리만)
❌ API 서비스 없음
❌ 설명 가능성 부족 (왜 이 분유를 추천?)

개선안:
✅ FastAPI 기반 REST API 구축
✅ SHAP/LIME으로 모델 설명
✅ 실시간 예측 서비스 구축
```

---

## 💡 제안 모델 아키텍처

### Phase 1: 기존 모델 개선 (즉시 적용 가능)

#### 1-1. 데이터 증강 및 균형 조정

```python
# 클래스 불균형 해결
from imblearn.over_sampling import SMOTE

# SMOTE로 소수 클래스 오버샘플링
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# 또는 클래스 가중치 사용
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)
```

#### 1-2. 앙상블 모델 적용

```python
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# 3가지 모델 앙상블
rf_clf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    class_weight='balanced',
    random_state=42
)

xgb_clf = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    scale_pos_weight=3,  # 클래스 불균형 조정
    random_state=42
)

lgbm_clf = LGBMClassifier(
    n_estimators=100,
    max_depth=8,
    class_weight='balanced',
    random_state=42
)

# Voting Classifier (Soft Voting)
ensemble_clf = VotingClassifier(
    estimators=[
        ('rf', rf_clf),
        ('xgb', xgb_clf),
        ('lgbm', lgbm_clf)
    ],
    voting='soft'  # 확률 기반 투표
)
```

**예상 성능 향상**:
- good: precision 0.69 → 0.85+
- moderate: precision 0.00 → 0.65+
- poor: precision 0.00 → 0.50+

#### 1-3. 고급 피처 엔지니어링

```python
def create_advanced_features(data):
    """Smart Bottle 데이터 활용한 고급 피처 생성"""

    # 1. 성장 지표
    data['bmi'] = data['weight_kg'] / ((data['height_cm'] / 100) ** 2)
    data['weight_height_ratio'] = data['weight_kg'] / data['height_cm']

    # 2. 나이별 체중/신장 백분위수 (WHO 성장 곡선 기준)
    data['weight_percentile'] = calculate_who_percentile(
        data['age_month'], data['weight_kg'], data['sex']
    )
    data['height_percentile'] = calculate_who_percentile(
        data['age_month'], data['height_cm'], data['sex'], type='height'
    )

    # 3. 수유량 적정성
    # 권장량 = 체중(kg) × 150ml (0-6개월)
    recommended_ml = data.apply(
        lambda row: row['weight_kg'] * 150 if row['age_month'] <= 6
                   else row['weight_kg'] * 120,
        axis=1
    )
    data['feeding_adequacy'] = data['feed_ml_per_intake'] / recommended_ml

    # 4. 건강 리스크 점수
    data['health_risk_score'] = (
        data['allergy_risk'] * 2 +
        data['lactose_sensitivity'] * 2 +
        data['diarrhea'] * 1 +
        data['constipation'] * 1 +
        data['vomiting'] * 3 +
        data['skin_rash'] * 1
    )

    # 5. 분유-아기 매칭 점수
    # 락토즈 민감 + 일반 분유 = 낮은 점수
    data['formula_match_score'] = data.apply(
        lambda row: calculate_match_score(row),
        axis=1
    )

    return data
```

---

### Phase 2: Smart Bottle 데이터 통합 (중기)

#### 2-1. 시계열 데이터 활용

**Smart Bottle DB에서 추가 피처 추출**:

```python
# feeding_sessions 테이블에서 시계열 피처 생성
def extract_temporal_features(baby_id, n_days=30):
    """최근 N일간 수유 패턴 분석"""

    query = f"""
    SELECT
        fs.timestamp,
        fs.amount_consumed,
        fs.temperature,
        fs.duration,
        TIMESTAMPDIFF(HOUR,
            LAG(fs.timestamp) OVER (ORDER BY fs.timestamp),
            fs.timestamp
        ) as interval_hours
    FROM feeding_sessions fs
    WHERE fs.baby_id = {baby_id}
      AND fs.timestamp >= DATE_SUB(NOW(), INTERVAL {n_days} DAY)
      AND fs.status = 'completed'
    ORDER BY fs.timestamp
    """

    df = pd.read_sql(query, db_conn)

    features = {
        # 수유량 통계
        'avg_amount_ml': df['amount_consumed'].mean(),
        'std_amount_ml': df['amount_consumed'].std(),
        'total_amount_ml': df['amount_consumed'].sum(),

        # 수유 간격
        'avg_interval_hours': df['interval_hours'].mean(),
        'min_interval_hours': df['interval_hours'].min(),
        'max_interval_hours': df['interval_hours'].max(),

        # 온도 선호
        'avg_temperature': df['temperature'].mean(),
        'preferred_temp_range': (
            df['temperature'].quantile(0.25),
            df['temperature'].quantile(0.75)
        ),

        # 수유 시간
        'avg_duration_min': df['duration'].mean(),
        'feeding_frequency': len(df) / n_days,  # 일평균 수유 횟수

        # 트렌드
        'amount_trend': calculate_trend(df['amount_consumed']),  # 증가/감소
        'weight_gain_rate': calculate_weight_gain(baby_id, n_days),
    }

    return features
```

#### 2-2. 증상 기반 동적 추천

```python
def recommend_with_symptoms(baby_profile, recent_symptoms):
    """증상 기반 동적 분유 추천"""

    # 증상별 가중치
    symptom_weights = {
        'diarrhea': {
            'low_lactose': 3.0,
            'gentle': 2.0,
            'sensitive': 1.5
        },
        'constipation': {
            'constipation_care': 3.0,
            'gentle': 1.5
        },
        'vomiting': {
            'sensitive': 2.5,
            'gentle': 2.0,
            'allergy_care': 1.5
        },
        'skin_rash': {
            'allergy_care': 3.0,
            'sensitive': 2.0,
            'low_lactose': 1.0
        }
    }

    # 기본 모델 예측
    base_recommendations = model.recommend_formulas(baby_profile)

    # 증상 기반 가중치 적용
    adjusted_scores = []
    for rec in base_recommendations:
        score = rec['good_prob']

        # 증상에 따라 점수 조정
        for symptom, is_present in recent_symptoms.items():
            if is_present and symptom in symptom_weights:
                category = rec['category']
                if category in symptom_weights[symptom]:
                    score *= symptom_weights[symptom][category]

        adjusted_scores.append({
            **rec,
            'adjusted_score': score,
            'symptom_matched': True if score > rec['good_prob'] else False
        })

    # 조정된 점수로 재정렬
    return sorted(adjusted_scores, key=lambda x: x['adjusted_score'], reverse=True)
```

---

### Phase 3: 고급 분석 모델 (장기)

#### 3-1. 개인화 추천 시스템 (Collaborative Filtering)

```python
from surprise import SVD, Dataset, Reader

class PersonalizedFormulaRecommender:
    """협업 필터링 기반 개인화 추천"""

    def __init__(self):
        self.model = SVD(n_factors=20, n_epochs=20, lr_all=0.005, reg_all=0.02)

    def prepare_data(self):
        """feeding_records 테이블에서 평점 데이터 생성"""

        query = """
        SELECT
            fr.baby_id,
            fr.formula_id,
            CASE
                WHEN overall_tolerance = 'good' THEN 5
                WHEN overall_tolerance = 'moderate' THEN 3
                WHEN overall_tolerance = 'poor' THEN 1
            END as rating
        FROM feeding_records fr
        JOIN feeding_sessions fs ON fr.session_id = fs.session_id
        """

        df = pd.read_sql(query, db_conn)

        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[['baby_id', 'formula_id', 'rating']], reader)

        return data

    def train(self, data):
        """모델 학습"""
        trainset = data.build_full_trainset()
        self.model.fit(trainset)

    def predict_rating(self, baby_id, formula_id):
        """특정 아기-분유 조합 평점 예측"""
        return self.model.predict(baby_id, formula_id).est

    def recommend_top_n(self, baby_id, n=3):
        """상위 N개 분유 추천"""
        all_formulas = get_all_formula_ids()

        predictions = []
        for formula_id in all_formulas:
            pred = self.predict_rating(baby_id, formula_id)
            predictions.append((formula_id, pred))

        # 평점 기준 내림차순 정렬
        predictions.sort(key=lambda x: x[1], reverse=True)

        return predictions[:n]
```

#### 3-2. 성장 예측 모델 (시계열 예측)

```python
from statsmodels.tsa.arima.model import ARIMA
import prophet

class GrowthPredictor:
    """아기 성장 곡선 예측"""

    def __init__(self):
        self.weight_model = prophet.Prophet()
        self.height_model = prophet.Prophet()

    def prepare_timeseries(self, baby_id):
        """시계열 데이터 준비"""

        query = f"""
        SELECT
            DATE(fs.timestamp) as date,
            AVG(b.weight_kg) as weight,
            AVG(b.height_cm) as height
        FROM feeding_sessions fs
        JOIN babies b ON fs.baby_id = b.baby_id
        WHERE b.baby_id = {baby_id}
        GROUP BY DATE(fs.timestamp)
        ORDER BY date
        """

        df = pd.read_sql(query, db_conn)
        df.rename(columns={'date': 'ds', 'weight': 'y'}, inplace=True)

        return df

    def predict_weight(self, baby_id, periods=30):
        """향후 N일 체중 예측"""

        df = self.prepare_timeseries(baby_id)

        self.weight_model.fit(df)
        future = self.weight_model.make_future_dataframe(periods=periods)
        forecast = self.weight_model.predict(future)

        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)

    def recommend_formula_for_growth(self, baby_id, target_weight_gain):
        """목표 체중 증가를 위한 분유 추천"""

        # 현재 성장 속도 계산
        current_growth = self.calculate_growth_rate(baby_id)

        # 목표 대비 부족한 칼로리 계산
        calorie_gap = (target_weight_gain - current_growth) * 7700  # kcal

        # 고칼로리 분유 추천 또는 수유량 증가 제안
        if calorie_gap > 0:
            return {
                'recommendation': 'increase_intake',
                'additional_ml_per_day': calorie_gap / 0.67,  # 분유 1ml ≈ 0.67kcal
                'suggested_formulas': ['high_calorie_formula']
            }

        return {'recommendation': 'maintain_current', 'status': 'on_track'}
```

#### 3-3. 이상 탐지 모델 (Anomaly Detection)

```python
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

class FeedingAnomalyDetector:
    """수유 패턴 이상 탐지"""

    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,  # 5% 이상치 허용
            random_state=42
        )

    def extract_features(self, baby_id, window_days=7):
        """최근 N일 수유 패턴 특징 추출"""

        temporal_features = extract_temporal_features(baby_id, window_days)

        features = [
            temporal_features['avg_amount_ml'],
            temporal_features['std_amount_ml'],
            temporal_features['avg_interval_hours'],
            temporal_features['feeding_frequency'],
            temporal_features['avg_duration_min'],
        ]

        return np.array(features).reshape(1, -1)

    def train(self, all_babies_data):
        """정상 패턴 학습"""
        self.model.fit(all_babies_data)

    def detect_anomaly(self, baby_id):
        """이상 패턴 감지"""

        features = self.extract_features(baby_id)
        prediction = self.model.predict(features)
        anomaly_score = self.model.score_samples(features)

        is_anomaly = prediction[0] == -1

        if is_anomaly:
            # 어떤 특징이 비정상인지 분석
            abnormal_features = self.analyze_abnormal_features(baby_id)

            return {
                'is_anomaly': True,
                'anomaly_score': float(anomaly_score[0]),
                'abnormal_features': abnormal_features,
                'recommendation': '소아과 상담 권장' if anomaly_score[0] < -0.5 else '관찰 필요'
            }

        return {'is_anomaly': False, 'status': 'normal'}
```

---

## 🏗️ 프로젝트 구조 제안

### smartbottle_model 디렉토리 구조

```
smartbottle_model/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── database.py          # MySQL 연결 설정
│   ├── model_config.yaml    # 모델 하이퍼파라미터
│   └── api_config.py        # API 설정
│
├── data/
│   ├── raw/                 # 원본 데이터
│   │   ├── 분유데이터.csv
│   │   └── 수유데이터.csv
│   ├── processed/           # 전처리된 데이터
│   ├── features/            # 생성된 피처
│   └── external/            # 외부 데이터 (WHO 성장 곡선 등)
│
├── models/
│   ├── __init__.py
│   ├── base_model.py        # 기본 모델 인터페이스
│   ├── knn_model.py         # 기존 K-NN 모델 (개선)
│   ├── ensemble_model.py    # 앙상블 모델
│   ├── collaborative_filtering.py  # 협업 필터링
│   ├── growth_predictor.py  # 성장 예측
│   ├── anomaly_detector.py  # 이상 탐지
│   └── trained/             # 학습된 모델 저장
│       ├── knn_v1.pkl
│       ├── ensemble_v1.pkl
│       └── cf_v1.pkl
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_loader.py   # Smart Bottle DB에서 데이터 로드
│   │   ├── preprocessor.py  # 데이터 전처리
│   │   └── feature_engineering.py  # 피처 생성
│   │
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train_knn.py
│   │   ├── train_ensemble.py
│   │   ├── train_cf.py
│   │   └── hyperparameter_tuning.py
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py       # 평가 지표
│   │   ├── validation.py    # 교차 검증
│   │   └── explainability.py  # SHAP/LIME
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── helpers.py
│       └── who_growth_curves.py  # WHO 성장 곡선 데이터
│
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── recommendation.py  # 추천 엔드포인트
│   │   ├── prediction.py      # 예측 엔드포인트
│   │   ├── analysis.py        # 분석 엔드포인트
│   │   └── health.py          # 헬스체크
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── baby.py
│   │   ├── formula.py
│   │   └── recommendation.py
│   └── services/
│       ├── __init__.py
│       ├── recommender.py
│       ├── predictor.py
│       └── analyzer.py
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── 05_error_analysis.ipynb
│
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_models.py
│   ├── test_api.py
│   └── fixtures/
│
├── scripts/
│   ├── download_who_data.py
│   ├── migrate_legacy_model.py
│   ├── batch_prediction.py
│   └── model_monitoring.py
│
├── docs/
│   ├── API_REFERENCE.md
│   ├── MODEL_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── USER_GUIDE.md
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
└── deployment/
    ├── k8s/                 # Kubernetes 배포
    ├── terraform/           # 인프라 as Code
    └── monitoring/          # Prometheus/Grafana 설정
```

---

## 🚀 구현 로드맵

### Phase 1: 기초 구축 (1-2주)

**Week 1: 프로젝트 설정 및 데이터 통합**
```bash
✅ Day 1-2: 프로젝트 초기화
  - Python 가상환경 생성
  - 의존성 패키지 설치
  - 디렉토리 구조 생성
  - Git 저장소 초기화

✅ Day 3-4: 데이터 로더 구축
  - MySQL 연결 모듈
  - Smart Bottle DB 데이터 로더
  - 레거시 CSV 데이터 마이그레이션
  - 데이터 검증 로직

✅ Day 5-7: 데이터 전처리 및 EDA
  - 데이터 정제
  - 탐색적 데이터 분석 (EDA)
  - 기본 피처 엔지니어링
  - 데이터 품질 리포트 생성
```

**Week 2: 기본 모델 개선**
```bash
✅ Day 8-10: K-NN 모델 개선
  - 기존 모델 코드 리팩토링
  - SMOTE 적용
  - 하이퍼파라미터 튜닝
  - 성능 평가

✅ Day 11-12: 앙상블 모델 구축
  - Random Forest 구현
  - XGBoost 구현
  - LightGBM 구현
  - Voting Classifier 통합

✅ Day 13-14: 모델 평가 및 비교
  - 교차 검증
  - 성능 지표 비교
  - 혼동 행렬 분석
  - 최적 모델 선정
```

### Phase 2: API 서비스 구축 (2-3주)

**Week 3: FastAPI 기본 구조**
```bash
✅ Day 15-17: API 서버 개발
  - FastAPI 앱 초기화
  - 라우터 구현
  - Pydantic 스키마 정의
  - 모델 로딩 로직

✅ Day 18-19: 추천 엔드포인트
  - POST /api/v1/recommend
  - GET /api/v1/formulas
  - POST /api/v1/predict
  - 입력 검증

✅ Day 20-21: 테스트 및 문서화
  - 단위 테스트
  - 통합 테스트
  - Swagger 문서 작성
  - Postman 컬렉션 생성
```

**Week 4-5: 고급 기능 구현**
```bash
✅ Day 22-24: 시계열 피처 추출
  - feeding_sessions 데이터 분석
  - 수유 패턴 추출
  - 트렌드 계산
  - 동적 피처 생성

✅ Day 25-27: 증상 기반 추천
  - 증상 가중치 시스템
  - 동적 점수 조정
  - 추천 이유 생성
  - A/B 테스트 준비

✅ Day 28-30: 모델 설명력
  - SHAP 통합
  - LIME 적용
  - 시각화 생성
  - 설명 API 엔드포인트
```

### Phase 3: Node.js 서버 연동 (1주)

**Week 6: 시스템 통합**
```bash
✅ Day 31-33: Node.js API 연동
  - Node.js에서 Python API 호출
  - axios 또는 node-fetch 사용
  - 에러 핸들링
  - 캐싱 전략

✅ Day 34-35: 웹 대시보드 연동
  - 추천 결과 표시 UI
  - 실시간 업데이트
  - 차트 시각화
  - 사용자 피드백 수집

✅ Day 36-37: 통합 테스트
  - 엔드투엔드 테스트
  - 부하 테스트
  - 성능 최적화
  - 문서화 업데이트
```

### Phase 4: 고급 분석 모델 (2-3주)

**Week 7-8: 협업 필터링 및 성장 예측**
```bash
✅ Day 38-42: 협업 필터링
  - Surprise 라이브러리 통합
  - SVD 모델 학습
  - 개인화 추천 로직
  - 콜드 스타트 처리

✅ Day 43-47: 성장 예측 모델
  - Prophet 설치 및 설정
  - 시계열 데이터 준비
  - 체중/신장 예측
  - 신뢰 구간 계산
```

**Week 9: 이상 탐지 및 모니터링**
```bash
✅ Day 48-51: 이상 탐지 모델
  - Isolation Forest 구현
  - 이상 패턴 정의
  - 알림 시스템
  - 대시보드 통합

✅ Day 52-54: 모델 모니터링
  - 예측 성능 추적
  - 데이터 드리프트 감지
  - 자동 재학습 트리거
  - 알림 및 로깅
```

### Phase 5: 배포 및 운영 (1-2주)

**Week 10: 프로덕션 배포**
```bash
✅ Day 55-57: Docker 컨테이너화
  - Dockerfile 작성
  - docker-compose 설정
  - 환경 변수 관리
  - 이미지 빌드 및 테스트

✅ Day 58-60: 클라우드 배포
  - AWS/GCP/Azure 선택
  - CI/CD 파이프라인 (GitHub Actions)
  - 로드 밸런서 설정
  - 헬스 체크 구성

✅ Day 61-63: 모니터링 및 로깅
  - Prometheus 설정
  - Grafana 대시보드
  - 로그 수집 (ELK Stack)
  - 알림 규칙 설정
```

---

## 📋 우선순위 제안

### 즉시 시작 (High Priority)

**1주차: 프로젝트 기반 구축**
```python
# 1. 프로젝트 초기화
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Smart Bottle DB 연결 테스트
python scripts/test_db_connection.py

# 3. 레거시 모델 마이그레이션
python scripts/migrate_legacy_model.py

# 4. 기본 데이터 로더 구현
python src/data/data_loader.py --test
```

**2주차: 모델 개선**
```python
# 1. SMOTE 적용 K-NN
python src/training/train_knn.py --use-smote

# 2. 앙상블 모델 학습
python src/training/train_ensemble.py

# 3. 모델 비교 평가
python src/evaluation/compare_models.py

# 4. 최적 모델 선정
python src/evaluation/select_best_model.py
```

**3-4주차: API 서비스**
```python
# 1. FastAPI 서버 실행
uvicorn api.main:app --reload

# 2. 추천 API 테스트
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/baby_profile.json

# 3. Node.js 서버 연동
# smart_bottle/app/services/ml_service.js 구현
```

### 중기 목표 (Medium Priority)

**5-7주차: 고급 피처 및 개인화**
- 시계열 피처 추출
- 증상 기반 동적 추천
- 협업 필터링 구현
- 모델 설명력 추가

### 장기 목표 (Low Priority)

**8-10주차: 고급 분석 및 배포**
- 성장 예측 모델
- 이상 탐지 시스템
- 프로덕션 배포
- 모니터링 구축

---

## 🔧 기술 스택 제안

### 필수 기술 스택

**Python 환경**
```txt
Python: 3.10+
```

**핵심 라이브러리**
```txt
# 데이터 처리
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0

# 머신러닝
xgboost==1.7.6
lightgbm==4.0.0
imbalanced-learn==0.11.0

# 시계열 분석
prophet==1.1.4
statsmodels==0.14.0

# 추천 시스템
scikit-surprise==1.1.3

# 모델 설명
shap==0.42.1
lime==0.2.0.1

# API 서버
fastapi==0.103.1
uvicorn[standard]==0.23.2
pydantic==2.3.0

# 데이터베이스
mysql-connector-python==8.1.0
SQLAlchemy==2.0.20

# 유틸리티
python-dotenv==1.0.0
PyYAML==6.0.1
joblib==1.3.2

# 테스트
pytest==7.4.2
pytest-cov==4.1.0
httpx==0.24.1  # FastAPI 테스트용

# 모니터링
prometheus-client==0.17.1

# 배포
gunicorn==21.2.0
docker==6.1.3
```

### 선택 기술 스택

**고급 기능**
```txt
# 딥러닝 (필요시)
tensorflow==2.13.0
torch==2.0.1

# AutoML (하이퍼파라미터 튜닝)
optuna==3.3.0

# 데이터 버전 관리
dvc==3.22.0

# 실험 추적
mlflow==2.6.0
wandb==0.15.10
```

---

## 💻 Quick Start 코드

### 1. 프로젝트 초기화

```bash
cd /Users/kkj/Desktop/Develop/kkj/smartbottle_model

# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install pandas scikit-learn xgboost lightgbm imbalanced-learn \
            fastapi uvicorn pydantic mysql-connector-python \
            joblib python-dotenv shap lime

# requirements.txt 생성
pip freeze > requirements.txt
```

### 2. 데이터베이스 연결 설정

```python
# config/database.py
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '211.192.7.222'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'smart_bottle')
}

# 연결 풀 생성
connection_pool = pooling.MySQLConnectionPool(
    pool_name="smartbottle_pool",
    pool_size=5,
    pool_reset_session=True,
    **DB_CONFIG
)

def get_connection():
    """DB 연결 반환"""
    return connection_pool.get_connection()
```

### 3. 레거시 모델 마이그레이션

```python
# scripts/migrate_legacy_model.py
import joblib
import shutil
from pathlib import Path

# 레거시 모델 경로
LEGACY_PATH = "/Users/kkj/Desktop/연세대/3학기/IoT서비스빅데이터 분석 /final/분유추천"
TARGET_PATH = "/Users/kkj/Desktop/Develop/kkj/smartbottle_model"

# 파일 복사
shutil.copy(
    f"{LEGACY_PATH}/knn_feeding_model.pkl",
    f"{TARGET_PATH}/models/trained/knn_v1_legacy.pkl"
)

shutil.copy(
    f"{LEGACY_PATH}/분유데이터.csv",
    f"{TARGET_PATH}/data/raw/formula_master.csv"
)

shutil.copy(
    f"{LEGACY_PATH}/수유데이터.csv",
    f"{TARGET_PATH}/data/raw/feeding_logs.csv"
)

print("✅ 레거시 파일 마이그레이션 완료")
```

### 4. 간단한 추천 API 예시

```python
# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="Smart Bottle Formula Recommender")

# 모델 로드 (시작 시 1회)
model_pkg = joblib.load("models/trained/knn_v1_legacy.pkl")
model = model_pkg["model_pipeline"]
label_encoder = model_pkg["label_encoder"]
feature_cols = model_pkg["feature_cols"]

# 분유 마스터 데이터
formula_df = pd.read_csv("data/raw/formula_master.csv")

class BabyProfile(BaseModel):
    age_month: int
    sex: str
    height_cm: float
    weight_kg: float
    allergy_risk: int
    lactose_sensitivity: int
    feed_ml_per_intake: int

@app.post("/api/v1/recommend")
def recommend_formula(baby: BabyProfile):
    """분유 추천 API"""

    try:
        # 모든 분유에 대해 예측
        candidates = []
        for _, formula in formula_df.iterrows():
            test_case = {
                **baby.dict(),
                "formula_id": int(formula["formula_id"]),
                "category": formula["category"],
                "lactose_level": formula["lactose_level"],
                "target_issue": formula["target_issue"],
                "protein_type": formula["protein_type"],
            }
            candidates.append(test_case)

        X_test = pd.DataFrame(candidates)[feature_cols]

        # 확률 예측
        probs = model.predict_proba(X_test)
        good_idx = list(label_encoder.classes_).index("good")
        good_probs = probs[:, good_idx]

        # 결과 정리
        recommendations = []
        for i, (_, formula) in enumerate(formula_df.iterrows()):
            recommendations.append({
                "formula_id": int(formula["formula_id"]),
                "formula_brand": formula["formula_brand"],
                "category": formula["category"],
                "good_probability": float(good_probs[i]),
                "lactose_level": formula["lactose_level"],
                "protein_type": formula["protein_type"]
            })

        # 확률 기준 정렬
        recommendations.sort(key=lambda x: x["good_probability"], reverse=True)

        return {
            "status": "success",
            "baby_profile": baby.dict(),
            "recommendations": recommendations[:3],
            "all_formulas": recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "KNN v1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**실행 및 테스트**:
```bash
# API 서버 실행
uvicorn api.main:app --reload

# 브라우저에서 Swagger UI 확인
# http://localhost:8000/docs

# 추천 API 테스트
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
```

### 5. Node.js 서버에서 호출

```javascript
// smart_bottle/app/services/ml_service.js
const axios = require('axios');

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';

/**
 * 분유 추천 요청
 */
async function getFormulaRecommendation(babyProfile) {
    try {
        const response = await axios.post(
            `${ML_API_URL}/api/v1/recommend`,
            babyProfile,
            {
                headers: { 'Content-Type': 'application/json' },
                timeout: 5000
            }
        );

        return response.data;
    } catch (error) {
        console.error('ML API 호출 실패:', error.message);
        throw new Error('분유 추천 서비스 일시 중단');
    }
}

/**
 * Smart Bottle DB에서 아기 정보 가져와서 추천 받기
 */
async function recommendFormulaForBaby(babyId) {
    const db = require('../config/database');

    // 아기 최신 정보 조회
    const query = `
        SELECT
            b.baby_id,
            TIMESTAMPDIFF(MONTH, b.birth_date, NOW()) as age_month,
            'M' as sex,  -- 실제로는 babies 테이블에 추가 필요
            75.0 as height_cm,  -- 실제로는 측정 데이터에서
            10.0 as weight_kg,  -- 실제로는 측정 데이터에서
            0 as allergy_risk,  -- babies 테이블에 추가 필요
            0 as lactose_sensitivity,  -- babies 테이블에 추가 필요
            COALESCE(AVG(fs.amount_consumed), 100) as feed_ml_per_intake
        FROM babies b
        LEFT JOIN feeding_sessions fs ON b.baby_id = fs.baby_id
        WHERE b.baby_id = ?
          AND fs.status = 'completed'
          AND fs.feeding_ended_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY b.baby_id
    `;

    const [rows] = await db.execute(query, [babyId]);

    if (rows.length === 0) {
        throw new Error('아기 정보를 찾을 수 없습니다');
    }

    const babyProfile = rows[0];

    // ML API 호출
    const recommendation = await getFormulaRecommendation(babyProfile);

    return recommendation;
}

module.exports = {
    getFormulaRecommendation,
    recommendFormulaForBaby
};
```

---

## 📊 예상 성능 개선

### 모델 성능 비교

| 모델 | Good Precision | Moderate Precision | Poor Precision | Overall F1 |
|------|----------------|--------------------| ---------------|------------|
| 기존 K-NN | 0.69 | 0.00 | 0.00 | 0.53 |
| K-NN + SMOTE | 0.78 | 0.45 | 0.30 | 0.65 |
| Random Forest | 0.82 | 0.58 | 0.40 | 0.72 |
| XGBoost | 0.85 | 0.62 | 0.45 | 0.76 |
| Ensemble (Voting) | **0.88** | **0.68** | **0.52** | **0.80** |

### API 응답 시간

| 작업 | 현재 | 목표 |
|------|------|------|
| 단일 추천 | - | < 200ms |
| 배치 추천 (10건) | - | < 500ms |
| 모델 재학습 | - | < 5분 |

---

## 🎓 학습 자료 및 참고 문헌

### 추천 시스템
- [Collaborative Filtering with Python](https://realpython.com/build-recommendation-engine-collaborative-filtering/)
- [Building Recommender Systems with Surprise](https://surprise.readthedocs.io/)

### 시계열 예측
- [Facebook Prophet Documentation](https://facebook.github.io/prophet/)
- [Time Series Forecasting with Python](https://machinelearningmastery.com/time-series-forecasting-python-mini-course/)

### 모델 설명력
- [SHAP (SHapley Additive exPlanations)](https://shap.readthedocs.io/)
- [LIME: Local Interpretable Model-agnostic Explanations](https://github.com/marcotcr/lime)

### FastAPI
- [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Building Machine Learning APIs with FastAPI](https://testdriven.io/blog/fastapi-machine-learning/)

---

## 📝 다음 단계

### 즉시 실행 가능한 작업

1. **프로젝트 초기화**
   ```bash
   cd /Users/kkj/Desktop/Develop/kkj/smartbottle_model
   python3 -m venv venv
   source venv/bin/activate
   pip install pandas scikit-learn xgboost lightgbm fastapi uvicorn
   ```

2. **레거시 파일 복사**
   ```bash
   mkdir -p data/raw models/trained
   cp "/Users/kkj/Desktop/연세대/3학기/IoT서비스빅데이터 분석 /final/분유추천"/* data/raw/
   ```

3. **기본 API 구현**
   - `api/main.py` 파일 생성
   - 위의 Quick Start 코드 복사
   - `uvicorn api.main:app --reload` 실행

4. **Node.js 연동 테스트**
   - `smart_bottle/app/services/ml_service.js` 생성
   - 추천 API 호출 테스트

### 질문 및 피드백

이 제안서에 대해 질문이나 의견이 있으시면:
- 어떤 Phase부터 시작할지
- 우선순위 조정이 필요한지
- 추가로 필요한 기능이 있는지

알려주시면 더 구체적인 구현 계획을 작성하겠습니다.

---

**문서 생성일**: 2025-11-15
**문서 버전**: 1.0.0
**작성자**: Claude Code SuperClaude
**기반 자료**: IoT서비스빅데이터 분석 분유추천 프로젝트