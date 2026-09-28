# GRIDMIND

## Cloud-Ready AI Energy Intelligence & Forecasting Platform

**Predict → Detect → Explain → Optimize**

GRIDMIND is an end-to-end energy intelligence platform designed to transform high-volume smart-grid data into **forecasting, anomaly detection, risk intelligence, and operational decisions**.

It combines a structured **Bronze → Silver → Gold data pipeline**, machine learning, FastAPI services, an AI Analyst interface, local S3-compatible object storage, and a 7-page Power BI Command Center.

> **500K+ smart-meter records → Data Lake → ML → Risk Intelligence → AI Analyst → Power BI**

---

## ⚡ What GRIDMIND Solves

Energy operations generate large volumes of consumption, weather, generation, asset, and grid-event data. Raw data alone does not provide operational visibility.

GRIDMIND converts that data into an intelligence layer that helps answer:

* What is happening across the grid?
* Where are abnormal conditions occurring?
* Which regions require attention?
* What demand is expected next?
* How much renewable generation is available?
* Which conditions should be prioritized for investigation?

The platform connects **data engineering → machine learning → risk analysis → decision intelligence** in a single workflow.

---

## 🏗️ Platform Architecture

```text
                    GRIDMIND
                       │
        ┌──────────────┴──────────────┐
        │                             │
   Energy Sources                Grid Operations
        │                             │
        ├── Smart Meters              ├── Grid Events
        ├── Weather                   └── Grid Assets
        └── Generation
                       │
                       ▼
              ┌─────────────────┐
              │   DATA LAKE     │
              │                 │
              │ Bronze → Silver │
              │      → Gold     │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Forecasting   Anomaly       Risk
       Engine      Detection    Intelligence
          │            │            │
          └────────────┼────────────┘
                       ▼
                AI ANALYST
                   FastAPI
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Web Platform        Power BI
                            Command Center
```

---

# 📊 Data Engineering

GRIDMIND processes multiple energy intelligence sources covering **2024–2025 hourly observations**.

| Dataset     | Records | Purpose                                       |
| ----------- | ------: | --------------------------------------------- |
| Smart Meter | 500,000 | Consumption & electrical measurements         |
| Weather     |  17,544 | Temperature, humidity, wind, solar & rainfall |
| Generation  |  17,544 | Solar, wind, hydro & thermal generation       |
| Grid Events |   5,000 | Operational events & severity                 |
| Grid Assets |   1,000 | Infrastructure & asset information            |

### Data Pipeline

```text
RAW DATA
   │
   ▼
BRONZE
Raw source datasets
   │
   ▼
SILVER
Cleaned + integrated
   │
   ▼
GOLD
Feature engineered
+ risk enriched
+ decision ready
```

### Gold Intelligence Layer

The final Gold dataset contains:

* **87,416 intelligence records**
* **57 analytical features**
* **5 regions**
* **0 missing records**
* **0 duplicate records**

Feature groups include:

```text
Demand
Weather
Generation
Renewables
Time Features
Lag Features
Rolling Features
Power Quality
Anomaly Signals
Risk Scores
Grid Status
Decision Priority
```

---

# 🤖 Machine Learning Layer

## 01 — Demand Forecasting

**Algorithm:** Random Forest Regressor

Configuration:

```text
Estimators:       150
Max Depth:        18
Min Samples Leaf: 2
Split Strategy:   Time-based 80/20
Prediction:       Next-hour regional demand
```

The forecasting engine uses historical demand, temporal patterns, electrical measurements and renewable-generation context to estimate upcoming demand.

### Key predictive features

```text
Hour
Demand_Rolling_168H
Demand_Lag_24H
Demand_Lag_1H
Demand_Lag_168H
Avg_Voltage_V
Demand_Rolling_24H
Avg_Power_Factor
Avg_Current_A
Renewable_Share_pct
```

The model artifact is stored locally for API and analytical integration.

---

## 02 — Grid Anomaly Detection

**Algorithm:** Isolation Forest

Configuration:

```text
Estimators:   200
Contamination: 2%
Scaler:       StandardScaler
Random State:  42
```

The anomaly engine identifies unusual combinations of operational and electrical conditions.

### Detection output

```text
Total Records       87,416
Detected Anomalies   1,749
Configured Rate       2.00%
```

Risk distribution:

| Risk Level | Records |
| ---------- | ------: |
| LOW        |  67,552 |
| MEDIUM     |  14,819 |
| HIGH       |   4,753 |
| CRITICAL   |     292 |

> **Note:** The 2% anomaly rate is the Isolation Forest contamination parameter used by the model. It should not be interpreted as a naturally observed grid failure rate.

---

# 🚨 Grid Risk Intelligence

GRIDMIND converts analytical signals into operational categories.

### Risk

```text
LOW
MEDIUM
HIGH
CRITICAL
```

### Decision Priority

```text
NORMAL
MONITOR
HIGH PRIORITY
IMMEDIATE ACTION
```

Current decision distribution:

| Priority         | Records |
| ---------------- | ------: |
| NORMAL           |  73,546 |
| MONITOR          |  12,591 |
| HIGH PRIORITY    |   1,262 |
| IMMEDIATE ACTION |      17 |

This layer connects machine-learning outputs with a more actionable operational structure.

---

# 🔌 FastAPI Intelligence API

GRIDMIND exposes the analytical platform through a production-style FastAPI backend.

### Core API groups

```text
/dashboard
/forecast
/risk
/ai
```

### Examples

```text
GET  /dashboard/summary
GET  /forecast/latest
GET  /risk/summary
GET  /risk/anomalies
POST /ai/ask
GET  /health
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🧠 AI Analyst

GRIDMIND includes an AI Analyst interface that converts natural-language questions into data-grounded analytical responses.

Example questions:

```text
What is the current grid risk situation?

Which region has the highest anomaly count?

Which region has the highest demand?

Which region has the highest renewable share?

What is the average peak-hour demand?
```

The current implementation uses a **rule-based, data-grounded analytical layer**.

The architecture is intentionally designed so the analyst layer can later be connected to an LLM provider such as:

```text
Ollama
Azure OpenAI
AWS Bedrock
Other enterprise LLM services
```

No external cloud AI service is required for the current local implementation.

---

# 🌐 GRIDMIND Web Platform

The FastAPI root route is presented as a product-style web interface rather than only an API documentation page.

### Interface sections

```text
Hero
↓
Platform Metrics
↓
Intelligence Engine
↓
Grid Risk Monitor
↓
Decision Flow
↓
AI Analyst
↓
Capabilities
↓
API Access
```

The interface provides a visual entry point to the platform while `/docs` remains available for technical API exploration.

---

# 📈 Power BI Command Center

GRIDMIND includes a **7-page Power BI Command Center** designed for executive and operational analysis.

### 01 — Executive Overview

High-level grid intelligence:

* Demand
* Anomalies
* Critical Risk
* Abnormal Grid
* Renewable Share
* Regional Demand
* Generation Mix
* Operational Priority

### 02 — Demand Forecast

* Actual vs Forecast
* Next-Hour Demand
* Forecast Error
* Peak Risk
* Feature Importance
* Regional Forecast Risk

### 03 — Grid Risk

* Risk Distribution
* Anomaly Rate
* Critical Risk
* High Risk
* Abnormal Grid
* Operational Attention

### 04 — Consumption Intelligence

* Hourly Demand
* Regional Consumption
* Weather–Demand Relationship
* Weekday vs Weekend
* Demand Volatility
* Power Factor

### 05 — Renewable Energy Intelligence

* Total Generation
* Renewable Generation
* Renewable Share
* Thermal Generation
* Generation/Demand Coverage
* Renewable Contribution

### 06 — Anomaly Investigation

* Region × Hour anomaly heatmap
* Anomaly timeline
* Risk distribution
* Abnormal conditions
* Critical case investigation
* Operational filters

### 07 — AI Decision Center

```text
Ask
↓
Explain
↓
Prioritize
↓
Act
```

The page provides an executive-facing decision intelligence interface around the AI Analyst capabilities.

---

# ☁️ Cloud-Ready Architecture

GRIDMIND currently runs locally and uses **SeaweedFS as an S3-compatible object-storage layer** for development.

The architecture follows cloud-oriented patterns:

```text
Object Storage
Data Lake
ML Artifacts
API Services
Analytics Layer
BI Layer
```

The platform is **designed for future AWS/Azure deployment**, but the current project does **not** claim production deployment on AWS or Azure.

---

# 🗂️ Project Structure

```text
GridMind/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── pipeline/
│   ├── data_quality.py
│   ├── build_energy_features.py
│   ├── build_silver.py
│   └── build_gold.py
│
├── models/
│   ├── demand_forecasting.py
│   ├── anomaly_detection.py
│   └── artifacts/
│
├── api/
│   ├── main.py
│   └── routes/
│       ├── dashboard.py
│       ├── forecast.py
│       ├── risk.py
│       └── ai.py
│
├── ai/
│   └── analyst.py
│
├── aws/
│   ├── upload_bronze.py
│   └── upload_processed.py
│
├── powerbi/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── tests/
│
├── docker/
│
└── README.md
```

---

# 🛠️ Technology Stack

### Data & Engineering

```text
Python
Pandas
NumPy
CSV / Data Lake Architecture
S3-Compatible Object Storage
SeaweedFS
```

### Machine Learning

```text
Scikit-learn
Random Forest
Isolation Forest
StandardScaler
Joblib
```

### Backend

```text
FastAPI
Pydantic
Uvicorn
REST APIs
CORS
```

### Analytics & BI

```text
Power BI
DAX
Data Modeling
Interactive Dashboards
Decision Intelligence
```

### Frontend

```text
HTML5
CSS3
JavaScript
Responsive UI
```

### Infrastructure

```text
Docker
Docker Desktop
S3-Compatible Storage
Cloud-Ready Architecture
```

---

# 🔄 End-to-End Workflow

```text
500K+ Smart Meter Records
          │
          ▼
     Data Quality
          │
          ▼
      Bronze Layer
          │
          ▼
      Silver Layer
          │
          ▼
       Gold Layer
          │
     ┌────┴────┐
     ▼         ▼
 Forecast   Anomaly
     │         │
     └────┬────┘
          ▼
    Risk Intelligence
          │
          ▼
      AI Analyst
          │
     ┌────┴─────┐
     ▼          ▼
   FastAPI    Power BI
     │       Command Center
     ▼          ▼
   Web       Decisions
 Platform
```

---

# 🎯 Business Intelligence Outcomes

GRIDMIND transforms a large operational dataset into a structured decision layer.

### From

```text
Raw Energy Data
```

### To

```text
Forecasted Demand
        +
Detected Anomalies
        +
Grid Risk
        +
Renewable Intelligence
        +
Operational Priority
        +
Natural-Language Analysis
```

This enables the platform to move beyond descriptive dashboards toward **predictive and decision-oriented energy intelligence**.

---

# 🔬 Key Engineering Highlights

* 500K+ smart-meter records
* 87K+ integrated intelligence records
* Bronze/Silver/Gold data architecture
* 57-feature Gold analytical layer
* Time-based ML forecasting
* Isolation Forest anomaly detection
* Risk scoring and decision prioritization
* FastAPI REST architecture
* Data-grounded AI Analyst
* S3-compatible local data lake
* 7-page Power BI Command Center
* Product-style web interface
* Docker-ready development environment
* Cloud-ready AWS/Azure architecture

---

# 🚀 Running GRIDMIND Locally

### 1. Navigate to the project

```powershell
cd D:\GridMind
```

### 2. Start the API

```powershell
python -m uvicorn api.main:app --reload
```

### 3. Open the platform

```text
http://127.0.0.1:8000/
```

### 4. Open API documentation

```text
http://127.0.0.1:8000/docs
```

### 5. Health check

```text
http://127.0.0.1:8000/health
```

---

# 🔐 Project Status

**Status: Operational Local Prototype / Portfolio-Ready**

```text
Data Engineering       ✓
Data Quality            ✓
Data Lake               ✓
Feature Engineering     ✓
Demand Forecasting      ✓
Anomaly Detection       ✓
Risk Intelligence       ✓
FastAPI                 ✓
AI Analyst              ✓
Web Interface           ✓
Power BI                ✓
Cloud-Ready Design      ✓
```

---

# 👩‍💻 Author

**Arifa Amir**

**Data Scientist | Data Analyst | Machine Learning | Python | SQL | BI**

GRIDMIND is designed as an end-to-end demonstration of how **data engineering, machine learning, APIs, AI-assisted analytics and business intelligence can be integrated into a single decision intelligence platform.**
