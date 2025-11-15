# Smart Bottle 프로젝트 전체 개요

## 📋 프로젝트 구조

이 시스템은 **3개의 연계 프로젝트**로 구성된 IoT 스마트 젖병 모니터링 시스템입니다.

```
Smart Bottle Ecosystem
├── Arduino smart_bottle      # 하드웨어/펌웨어 계층
├── smart_bottle              # 백엔드 서버 계층
└── smartbottle_model         # 데이터 분석 계층 (개발 예정)
```

---

## 🔗 프로젝트 간 연계성

### 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart Bottle System                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Arduino/ESP32]  ←──Socket.IO──→  [Node.js Server]         │
│   (Hardware)         Real-time       (Backend API)           │
│      ↓                                      ↓                │
│  Sensors:                            MySQL Database          │
│  - MLX90614 (온도)                         ↓                │
│  - HX711 (무게)                      Web Dashboard           │
│  - LED/Buzzer                              ↓                 │
│      ↓                            [smartbottle_model]        │
│  Real-time Data  ──────────────→   ML/Data Analysis          │
│                                     (개발 예정)              │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 흐름

1. **Arduino → Server**: 센서 데이터 실시간 전송 (Socket.IO)
2. **Server → Database**: 수유 기록 저장 (MySQL)
3. **Server → Client**: 웹 대시보드 업데이트 (Socket.IO)
4. **Database → Model**: 데이터 분석 및 예측 (예정)

---

## 📁 프로젝트 1: Arduino smart_bottle

### 위치
```
/Users/kkj/Documents/Arduino/smart_bottle
```

### 역할
**하드웨어 펌웨어 계층** - ESP32 기반 IoT 디바이스

### 핵심 기능
- ✅ 실시간 온도 측정 (MLX90614 센서)
- ✅ 무게 측정 (HX711 I2C 로드셀)
- ✅ 듀얼 센서 지원 (HX711 + RFP602)
- ✅ WiFi 연결 및 Socket.IO 통신
- ✅ 수유 상태 머신 관리
- ✅ LED/부저 피드백 시스템

### 기술 스택
```cpp
Platform:  ESP32
Language:  C++ (Arduino)
Libraries:
  - WiFi.h
  - SocketIOclient.h
  - Adafruit_MLX90614.h
  - DFRobot_HX711_I2C.h
  - ArduinoJson.h
```

### 하드웨어 구성

| 컴포넌트 | 핀 번호 | 용도 |
|---------|--------|------|
| MLX90614 | GPIO 21/22 (I2C) | 비접촉 온도 센서 |
| HX711 | GPIO 21/22 (I2C) | 무게 센서 (1kg 로드셀) |
| RFP602 | GPIO 32 (ADC) | 아날로그 압력 센서 (백업) |
| Green LED | GPIO 4 | 적정 온도 표시 (35-43°C) |
| Yellow LED | GPIO 5 | 저온 경고 (<35°C) |
| Red LED | GPIO 12 | 고온 경고 (>43°C) |
| Buzzer | GPIO 13 | 고온 알림 (2000Hz) |

### 상태 머신

```
IDLE → READY → BOTTLE_PLACED → FEEDING → COMPLETED → IDLE
  ↓       ↓          ↓              ↓          ↓
버튼대기  무게감지   온도측정      들어올림   소비량계산
```

### Socket.IO 이벤트 (Device → Server)

| 이벤트 | 데이터 | 설명 |
|-------|--------|-----|
| `device:connect` | device_uuid, device_name, baby_id | 디바이스 등록 |
| `feeding:start` | device_uuid, baby_id, timestamp | 수유 시작 |
| `bottle:placed` | weight, temperature, timestamp | 젖병 배치 |
| `feeding:pickup` | timestamp | 젖병 들어올림 |
| `feeding:end` | initial_weight, final_weight, duration | 수유 완료 |
| `temperature:update` | temperature, timestamp | 온도 업데이트 |
| `weight:tare:response` | success, message | 영점 조정 응답 |
| `weight:get:response` | weight, timestamp | 무게 조회 응답 |

### Socket.IO 이벤트 (Server → Device)

| 이벤트 | 데이터 | 설명 |
|-------|--------|-----|
| `device:connected` | deviceInfo | 연결 확인 |
| `feeding:ready` | session_id, timestamp | 세션 생성 완료 |
| `led:control` | color, action | LED 제어 |
| `feeding:completed` | session_id, result | 수유 완료 확인 |
| `weight:tare` | - | 영점 조정 요청 |
| `weight:get` | - | 무게 조회 요청 |
| `error` | message | 에러 메시지 |

### 설정 파일
```cpp
// WiFi 설정 (smart_bottle.ino:9-10)
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

// 서버 설정 (smart_bottle.ino:13-14)
const char* socketServer = "192.168.0.17";  // Node.js 서버 IP
const int socketPort = 3000;

// 디바이스 설정 (smart_bottle.ino:18)
const int baby_id = 1;
String device_uuid = WiFi.macAddress();  // 자동 생성
```

---

## 📁 프로젝트 2: smart_bottle (Node.js Server)

### 위치
```
/Users/kkj/Desktop/Develop/kkj/smart_bottle
```

### 역할
**백엔드 서버 계층** - 실시간 통신, 데이터베이스, 웹 인터페이스

### 핵심 기능
- ✅ Socket.IO 실시간 양방향 통신
- ✅ MySQL 데이터베이스 관리
- ✅ 수유 세션 자동화
- ✅ 디바이스 관리 (등록/캘리브레이션)
- ✅ 웹 대시보드 제공
- 🔄 REST API (개발 중)
- 🔄 데이터 분석 및 시각화 (예정)

### 기술 스택
```javascript
Runtime:     Node.js 18+
Framework:   Express.js 4.16.1
Real-time:   Socket.IO 4.8.1
Database:    MySQL 8.0
Template:    EJS 3.1.8
Logging:     Winston 3.8.2
Process:     PM2 (Cluster Mode)
```

### 프로젝트 구조

```
smart_bottle/
├── app/
│   ├── controllers/      # 비즈니스 로직
│   ├── models/           # 데이터 모델
│   ├── services/         # 서비스 계층
│   │   ├── device_service.js
│   │   └── feeding_service.js
│   ├── socket/           # Socket.IO 핸들러
│   │   └── socket_handler.js  # 9가지 이벤트 처리
│   └── views/            # EJS 템플릿
├── routes/               # 라우트 정의
│   ├── index_route.js
│   ├── dashboard_route.js
│   ├── device_route.js
│   ├── admin_route.js
│   └── api_route.js
├── config/
│   ├── database.js       # MySQL 연결 풀
│   └── env.js            # 환경변수 로더
├── database/
│   └── init_db.sql       # 데이터베이스 초기화
├── bin/
│   └── www               # 서버 진입점
├── app.js                # Express 앱 설정
└── package.json
```

### 데이터베이스 스키마 (7 Tables)

#### 1. users - 사용자 정보
```sql
user_id (PK)
email (UNIQUE)
password
name
created_at
```

#### 2. babies - 아기 정보
```sql
baby_id (PK)
user_id (FK)
name
birth_date
gender
weight_at_birth
created_at
```

#### 3. devices - IoT 디바이스 등록
```sql
device_id (PK)
user_id (FK)
device_uuid (UNIQUE)  -- ESP32 MAC 주소
device_name
bottle_weight         -- 젖병 공병 무게 (중요!)
is_online
socket_id
last_connected
created_at
updated_at
```

#### 4. feeding_sessions - 실시간 수유 세션
```sql
session_id (PK)
device_id (FK)
baby_id (FK)
status                -- ready/bottle_placed/in_progress/completed/cancelled
button_pressed_at
bottle_placed_at
feeding_started_at
feeding_ended_at
initial_weight
final_weight
amount_consumed       -- 실제 섭취량
temperature
duration
created_at
updated_at
```

#### 5. feeding_records - 수유 기록
```sql
feeding_id (PK)
session_id (FK)
baby_id (FK)
device_id (FK)
amount_consumed
temperature
duration
timestamp
notes
created_at
```

#### 6. formula_inventory - 분유 재고 관리
```sql
inventory_id (PK)
user_id (FK)
current_stock
daily_average
days_remaining
updated_at
```

#### 7. feeding_stats_daily - 일별 통계
```sql
stat_id (PK)
baby_id (FK)
date (UNIQUE)
total_feedings
total_amount
avg_amount
avg_temperature
avg_duration
created_at
```

### Socket.IO 핸들러 (socket_handler.js)

**관리하는 이벤트 (9개)**:
1. `device:connect` - 디바이스 연결 및 등록
2. `client:connect` - 웹 클라이언트 연결
3. `feeding:start` - 수유 세션 시작
4. `bottle:placed` - 젖병 배치 (무게/온도 기록)
5. `temperature:update` - 온도 업데이트
6. `feeding:pickup` - 수유 시작 (젖병 들어올림)
7. `feeding:end` - 수유 완료 (소비량 계산)
8. `weight:tare:response` - 무게 캘리브레이션 응답
9. `weight:get:response` - 무게 조회 응답

**핵심 로직**:
- Connection Maps로 디바이스/클라이언트 관리
- 자동 젖병 무게 차감 (정확한 소비량 측정)
- 온도 기반 LED 제어 (35-43°C 안전 범위)
- 실시간 웹 클라이언트 브로드캐스트

### 서버 설정

**데이터베이스 연결**:
```javascript
// config/database.js
host: '211.192.7.222',
port: 3306,
database: 'smart_bottle',
connectionLimit: 10,
waitForConnections: true,
queueLimit: 0
```

**서버 실행**:
```bash
# 개발 모드
npm run dev

# 프로덕션 모드
npm run prod

# PM2 클러스터 모드
npm run pm2:prod
```

### 환경 변수 (.env.{environment})

```bash
# Database
DB_HOST=211.192.7.222
DB_PORT=3306
DB_USER=username
DB_PASSWORD=password
DB_NAME=smart_bottle

# Application
NODE_ENV=production
PORT=3000
APP_STATUS=active
MEDIA_PATH=/uploads
```

---

## 📁 프로젝트 3: smartbottle_model (현재 프로젝트)

### 위치
```
/Users/kkj/Desktop/Develop/kkj/smartbottle_model
```

### 현재 상태
**빈 IntelliJ IDEA 프로젝트** - 초기 설정 단계

### 예상 역할
프로젝트 이름으로 추정되는 가능한 용도:

1. **머신러닝 모델 개발**
   - 수유 패턴 예측
   - 이상 감지 (섭취량 급변, 온도 이상)
   - 성장 곡선 예측

2. **데이터 분석**
   - 수유 통계 분석
   - 또래 비교 분석
   - 분유 소비 예측

3. **API 서버**
   - 데이터 분석 REST API
   - 예측 모델 서빙
   - 보고서 생성 서비스

4. **ETL 파이프라인**
   - 데이터 수집 및 전처리
   - 특징 추출
   - 데이터 웨어하우스 구축

### 제안 기술 스택

#### Option 1: Python (머신러닝/데이터 분석)
```python
Language:  Python 3.10+
Framework: FastAPI / Flask
ML:        scikit-learn, TensorFlow, PyTorch
Data:      pandas, numpy
DB:        SQLAlchemy (MySQL connector)
```

#### Option 2: Java (엔터프라이즈 백엔드)
```java
Language:  Java 17+
Framework: Spring Boot
ORM:       Spring Data JPA
DB:        MySQL Driver
```

#### Option 3: Node.js (마이크로서비스)
```javascript
Language:  TypeScript
Framework: NestJS / Express
ML:        TensorFlow.js
DB:        Sequelize / TypeORM
```

### 제안 프로젝트 구조 (Python 예시)

```
smartbottle_model/
├── src/
│   ├── models/              # ML 모델
│   │   ├── feeding_predictor.py
│   │   ├── anomaly_detector.py
│   │   └── growth_analyzer.py
│   ├── data/
│   │   ├── preprocessor.py
│   │   ├── feature_engineering.py
│   │   └── data_loader.py
│   ├── api/
│   │   ├── app.py           # FastAPI 앱
│   │   ├── routes/
│   │   └── schemas/
│   ├── utils/
│   │   ├── database.py
│   │   └── config.py
│   └── tests/
├── notebooks/               # Jupyter 노트북
│   ├── exploratory_analysis.ipynb
│   └── model_training.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/              # 학습된 모델 저장
├── requirements.txt
├── Dockerfile
└── README.md
```

### 데이터 연계 방안

#### MySQL에서 데이터 가져오기
```python
# src/data/data_loader.py
import mysql.connector
import pandas as pd

class SmartBottleDataLoader:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='211.192.7.222',
            port=3306,
            database='smart_bottle',
            user='username',
            password='password'
        )

    def get_feeding_records(self, baby_id, start_date, end_date):
        query = """
        SELECT
            fr.timestamp,
            fr.amount_consumed,
            fr.temperature,
            fr.duration,
            b.birth_date
        FROM feeding_records fr
        JOIN babies b ON fr.baby_id = b.baby_id
        WHERE fr.baby_id = %s
          AND fr.timestamp BETWEEN %s AND %s
        ORDER BY fr.timestamp
        """
        return pd.read_sql(query, self.conn, params=(baby_id, start_date, end_date))

    def get_daily_stats(self, baby_id):
        query = """
        SELECT * FROM feeding_stats_daily
        WHERE baby_id = %s
        ORDER BY date DESC
        """
        return pd.read_sql(query, self.conn, params=(baby_id,))
```

#### 예측 모델 예시
```python
# src/models/feeding_predictor.py
from sklearn.ensemble import RandomForestRegressor
import numpy as np

class FeedingPredictor:
    """다음 수유 시간 및 양 예측"""

    def __init__(self):
        self.model = RandomForestRegressor()

    def prepare_features(self, df):
        """특징 추출"""
        features = {
            'hour_of_day': df['timestamp'].dt.hour,
            'day_of_week': df['timestamp'].dt.dayofweek,
            'age_in_days': (df['timestamp'] - df['birth_date']).dt.days,
            'time_since_last_feeding': df['timestamp'].diff().dt.seconds / 3600,
            'avg_last_3_feedings': df['amount_consumed'].rolling(3).mean(),
            'temperature': df['temperature'],
        }
        return pd.DataFrame(features)

    def predict_next_feeding(self, baby_id):
        """다음 수유 시간과 예상량 예측"""
        # 최근 데이터 로드
        recent_data = self.data_loader.get_feeding_records(baby_id, days=30)

        # 특징 추출
        X = self.prepare_features(recent_data)

        # 예측
        predicted_time = self.model.predict(X[-1:])
        predicted_amount = self.amount_model.predict(X[-1:])

        return {
            'next_feeding_in_hours': predicted_time[0],
            'predicted_amount_ml': predicted_amount[0]
        }
```

---

## 🔄 시스템 워크플로우

### 1. 수유 세션 전체 흐름

```
1. [Arduino] 버튼 감지
   ↓ Socket.IO: feeding:start

2. [Server] 수유 세션 생성 (status: ready)
   ↓ feeding_sessions 테이블 INSERT
   ↓ Socket.IO: feeding:ready

3. [Arduino] 젖병 배치 감지
   ↓ 무게/온도 측정
   ↓ Socket.IO: bottle:placed

4. [Server] 초기 데이터 기록 (status: bottle_placed)
   ↓ feeding_sessions 테이블 UPDATE
   ↓ LED 제어 명령 전송
   ↓ Socket.IO: led:control

5. [Arduino] LED 점등 (온도에 따라)
   ↓ 젖병 들어올림 감지
   ↓ Socket.IO: feeding:pickup

6. [Server] 수유 시작 기록 (status: in_progress)
   ↓ feeding_started_at 타임스탬프

7. [Arduino] 2초마다 온도 업데이트
   ↓ Socket.IO: temperature:update

8. [Server] 실시간 브로드캐스트
   ↓ 웹 대시보드 업데이트

9. [Arduino] 젖병 놓기 감지
   ↓ 최종 무게 측정
   ↓ Socket.IO: feeding:end

10. [Server] 소비량 계산 및 저장
    ↓ amount_consumed = (initial_weight - final_weight) - bottle_weight
    ↓ feeding_sessions 테이블 UPDATE (status: completed)
    ↓ feeding_records 테이블 INSERT
    ↓ feeding_stats_daily 테이블 집계 업데이트
    ↓ Socket.IO: feeding:completed

11. [Model] 데이터 분석 (예정)
    ↓ 패턴 분석
    ↓ 예측 모델 업데이트
```

### 2. 디바이스 연결 흐름

```
1. [Arduino] WiFi 연결
   ↓ Socket.IO 서버 연결
   ↓ Socket.IO: device:connect

2. [Server] 디바이스 확인/등록
   ↓ devices 테이블 조회 (device_uuid)
   ↓ 없으면 INSERT, 있으면 UPDATE
   ↓ is_online = true
   ↓ socket_id 저장
   ↓ last_connected 업데이트
   ↓ Socket.IO: device:connected

3. [Arduino] 연결 확인 수신
   ↓ 정상 동작 시작
```

### 3. 무게 캘리브레이션 흐름

```
1. [Web] 캘리브레이션 요청
   ↓ Socket.IO: weight:tare

2. [Server] 디바이스로 전달
   ↓ Socket.IO: weight:tare

3. [Arduino] 영점 조정 수행
   ↓ scale.setCalibration()
   ↓ Socket.IO: weight:tare:response

4. [Server] 결과 전달
   ↓ 웹 클라이언트로 브로드캐스트
```

---

## 🎯 개발 로드맵

### Phase 1: 기본 시스템 구축 (완료 ✅)
- ✅ Arduino 펌웨어 개발
- ✅ Node.js 서버 구축
- ✅ MySQL 데이터베이스 설계
- ✅ Socket.IO 실시간 통신
- ✅ 기본 웹 인터페이스

### Phase 2: 기능 확장 (진행 중 🔄)
- 🔄 REST API 개발
- 🔄 사용자 인증 (JWT)
- 🔄 다중 아기 관리
- 🔄 실시간 대시보드 개선
- 🔄 데이터 시각화 (차트)

### Phase 3: 데이터 분석 (예정 📋)
- 📋 smartbottle_model 프로젝트 초기화
- 📋 수유 패턴 분석
- 📋 이상 감지 시스템
- 📋 성장 곡선 예측
- 📋 또래 비교 기능

### Phase 4: 고도화 (예정 📋)
- 📋 모바일 앱 개발 (React Native)
- 📋 푸시 알림 시스템
- 📋 음성 피드백 (TTS)
- 📋 클라우드 배포 (AWS/GCP)
- 📋 CI/CD 파이프라인

---

## 🛠️ 개발 환경 설정

### Arduino 프로젝트

```bash
# Arduino IDE 설치
# ESP32 보드 매니저 추가
# 라이브러리 설치:
- Adafruit MLX90614
- DFRobot HX711 I2C
- SocketIOclient
- ArduinoJson

# WiFi/서버 설정
smart_bottle.ino 파일 수정:
- Line 9-10: WiFi SSID/비밀번호
- Line 13-14: 서버 IP/포트
```

### Node.js 서버

```bash
cd /Users/kkj/Desktop/Develop/kkj/smart_bottle

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env.development
# .env.development 파일 수정 (DB 정보)

# 데이터베이스 초기화
npm run db:init

# 개발 서버 실행
npm run dev

# 프로덕션 실행
npm run prod
```

### smartbottle_model (초기 설정 필요)

```bash
cd /Users/kkj/Desktop/Develop/kkj/smartbottle_model

# Python 프로젝트 초기화 예시
python -m venv venv
source venv/bin/activate

# 의존성 설치 (requirements.txt 생성 후)
pip install -r requirements.txt

# Jupyter 노트북 실행
jupyter notebook
```

---

## 📊 주요 메트릭

### 시스템 성능
- Socket.IO 지연시간: < 100ms
- 센서 샘플링: 무게 1초, 온도 2초
- 데이터베이스 응답: < 50ms
- 웹 대시보드 업데이트: 실시간

### 측정 정확도
- 무게 측정: ±3% (HX711)
- 온도 측정: ±0.5°C (MLX90614)
- 소비량 계산: 젖병 무게 자동 차감

### 안전 범위
- 적정 온도: 35-43°C (Green LED)
- 경고 온도: <35°C (Yellow LED)
- 위험 온도: >43°C (Red LED + Buzzer)

---

## 📚 문서 및 참고자료

### Arduino 프로젝트
- `/Users/kkj/Documents/Arduino/smart_bottle/README.md`
- `/Users/kkj/Documents/Arduino/smart_bottle/CALIBRATION_GUIDE.md`
- `/Users/kkj/Documents/Arduino/smart_bottle/SENSOR_TEST_README.md`

### Node.js 서버
- `/Users/kkj/Desktop/Develop/kkj/smart_bottle/README.md`
- `/Users/kkj/Desktop/Develop/kkj/smart_bottle/SETUP.md`
- `/Users/kkj/Desktop/Develop/kkj/smart_bottle/docs/architecture.md`

### 현재 프로젝트
- `PROJECT_OVERVIEW.md` (이 문서)

---

## 🔐 보안 고려사항

### 데이터베이스
- 외부 접근 제한 (211.192.7.222:3306)
- 사용자 비밀번호 해싱 필요
- Connection pooling으로 연결 관리

### 통신
- Socket.IO 인증 구현 필요
- HTTPS/WSS 암호화 적용 필요
- CORS 설정 검토

### Arduino
- WiFi 자격 증명 하드코딩 회피
- OTA (Over-The-Air) 업데이트 고려

---

## 🚀 Quick Start

### 1. 전체 시스템 시작 순서

```bash
# 1단계: 데이터베이스 준비
# MySQL 서버가 211.192.7.222:3306에서 실행 중인지 확인

# 2단계: Node.js 서버 시작
cd /Users/kkj/Desktop/Develop/kkj/smart_bottle
npm run dev

# 3단계: Arduino 업로드
# Arduino IDE에서 smart_bottle.ino 열기
# WiFi/서버 설정 확인
# ESP32에 업로드

# 4단계: 웹 대시보드 접속
# http://localhost:3000
```

### 2. 테스트 시나리오

```
1. 시리얼 모니터 확인 (Arduino)
   - WiFi 연결 확인
   - Socket.IO 연결 확인

2. 웹 대시보드에서 디바이스 상태 확인
   - 디바이스 온라인 상태

3. 수유 프로세스 테스트
   - 버튼 누르기 (또는 무게 감지)
   - 젖병 올려놓기
   - LED 색상 확인 (온도 피드백)
   - 젖병 들어올리기
   - 2분 후 젖병 내려놓기

4. 데이터 확인
   - 웹 대시보드에서 수유 기록 확인
   - 데이터베이스 feeding_records 테이블 확인
```

---

## 💡 향후 smartbottle_model 프로젝트 제안

### 1. 수유 패턴 분석
```python
# 목표: 아기의 수유 패턴 파악
- 시간대별 수유량 분석
- 요일별 패턴 인식
- 계절별 변화 추적
```

### 2. 이상 감지
```python
# 목표: 건강 이상 조기 발견
- 갑작스러운 수유량 감소 감지
- 비정상 온도 선호도 변화 감지
- 수유 간격 이상 패턴 감지
```

### 3. 성장 예측
```python
# 목표: 아기 성장 곡선 예측
- 체중 증가 예측
- 발달 단계별 수유량 예측
- 분유 소비량 예측
```

### 4. 추천 시스템
```python
# 목표: 개인화된 수유 가이드
- 최적 수유 시간 추천
- 적정 수유량 가이드
- 분유 구매 시기 알림
```

### 5. 비교 분석
```python
# 목표: 또래 비교 및 벤치마킹
- 같은 월령 평균 비교
- 성장 퍼센타일 계산
- 발달 마일스톤 추적
```

---

## 📞 연락 및 지원

이 프로젝트는 현재 개발 중이며, 지속적으로 업데이트됩니다.

**프로젝트 위치**:
- Arduino: `/Users/kkj/Documents/Arduino/smart_bottle`
- Server: `/Users/kkj/Desktop/Develop/kkj/smart_bottle`
- Model: `/Users/kkj/Desktop/Develop/kkj/smartbottle_model`

**주요 설정 파일**:
- Arduino WiFi: `smart_bottle.ino` (Line 9-10)
- Arduino Server: `smart_bottle.ino` (Line 13-14)
- Server DB: `service.config.js` (PM2 설정)
- Server Env: `.env.development` / `.env.production`

---

**문서 생성일**: 2025-11-15
**문서 버전**: 1.0.0
**마지막 업데이트**: 프로젝트 초기 분석 완료