# 🚆 SmartTrain ETA Predictor

An AI-based train delay and ETA prediction dashboard that uses historical Indian railway data, route characteristics, weather conditions, and congestion-related features to estimate train arrival delays and explain the major contributing factors.

> **SmartTrain is designed to go beyond simply showing whether a train is late — it explores how existing delay, route conditions, weather, and congestion can affect the expected arrival time.**

## ✨ Key Features

- 📊 **Historical train-delay analysis** using 1.28M+ train-station records from September 2024
- ⏱️ **ETA prediction** based on the train's previous-station delay
- 🛤️ **Route-aware features** including station coordinates, distance, and section travel time
- 🌧️ **Weather features** including rainfall, temperature, and visibility
- 🚦 **Congestion scoring** using train frequency and historical section delay
- 🔎 **Explainability** showing the major factors associated with predicted delay
- 🌫️ **Fog disruption simulation** for what-if analysis
- 📈 **Historical validation** comparing predicted and recorded delay
- 🖥️ **Interactive Streamlit dashboard**
- ☁️ **Deployment-ready** with GitHub and Streamlit Community Cloud

## 🧠 How It Works

```text
Historical Train Data
        ↓
Data Preprocessing
        ↓
Route & Station Features
        ↓
Weather + Congestion Features
        ↓
Baseline + XGBoost Evaluation
        ↓
Explainability
        ↓
SmartTrain Dashboard
```

### Prediction Features

- Current delay
- Distance from previous station
- Historical section travel time
- Rainfall
- Temperature
- Visibility
- Congestion score
- Hour of day
- Day of week

## 📁 Dataset

The project uses historical Indian railway data covering **September 1–30, 2024**.

- **1,282,325 train-station records**
- Train number
- Date
- Station
- Scheduled arrival/departure
- Actual arrival/departure
- Arrival/departure delay

The project also enriches the data with station coordinates, historical weather information, route features, and congestion-related features.

## 📊 Model Evaluation

A simple baseline was evaluated against an XGBoost regression model using a chronological train/test split.

| Metric | Result |
|---|---:|
| Dataset records | 1,282,325 |
| Dataset period | September 1–30, 2024 |
| Baseline Test MAE | **16.34 min** |
| XGBoost Test MAE | **17.20 min** |
| Difference | **+0.86 min** |
| XGBoost improvement over baseline | **-5.26%** |
| Best approach in current validation | **Baseline** |

The baseline currently performs better than the tested XGBoost configuration. This result is retained honestly rather than presenting ML as better simply because it is more complex.

### Important interpretation

The current baseline uses the **previous-station observed delay** as the current-delay signal for estimating the next station's arrival. The dashboard therefore uses the validated baseline for its primary ETA rather than claiming that XGBoost is the deployed prediction model.

## 🔎 Explainability

The feature-importance analysis showed that **current delay** is the strongest feature in the evaluated XGBoost model, followed by congestion and route-related features.

The dashboard also provides a human-readable "Top Reason for Delay" based on the available journey factors.

## 🌫️ Disruption Simulation

The dashboard includes a fog/visibility **what-if simulation**.

Users can modify simulated visibility and observe how the estimated arrival time changes.

> The disruption simulation is a scenario analysis and is **not included in the verified baseline MAE**.

## 🖥️ Dashboard

The Streamlit dashboard allows users to select:

1. Train
2. Date
3. Station

It then displays:

- Predicted arrival time
- Expected delay range
- Previous-station delay
- Congestion score
- Distance from previous station
- Section travel time
- Top reason for delay
- Historical validation
- Fog disruption simulation

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Data processing and ML pipeline |
| **Pandas** | Data cleaning and feature engineering |
| **XGBoost** | Delay prediction model evaluation |
| **Open-Meteo API** | Historical weather data |
| **DuckDB** | Efficient analytical querying |
| **PyArrow / Parquet** | Compact dashboard data storage |
| **Streamlit** | Interactive dashboard |
| **GitHub** | Version control and source hosting |
| **Streamlit Community Cloud** | Deployment |

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/VaishnaviKadwad/smarttrain-eta-predictor.git
cd smarttrain-eta-predictor
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the dashboard

```bash
streamlit run app.py
```

The application will open in your browser at the local Streamlit address shown in the terminal.

## 📂 Repository Structure

```text
smarttrain-eta-predictor/
│
├── app.py
├── requirements.txt
├── final_dashboard_data.parquet
└── README.md
```

## 🔮 Future Scope

The current project is a validated prototype. The next stage can turn it into a more complete real-world passenger application by adding:

- 🔴 Live/current railway data integration
- 🗄️ PostgreSQL or another production database
- ⚡ FastAPI prediction backend
- 🎨 Next.js + Tailwind frontend
- 🗺️ Interactive railway route maps
- 🧠 Improved delay-propagation and historical features
- 📡 Continuous ETA updates
- 🔔 Passenger notifications
- 🌦️ Real-time weather integration
- 🤖 Further model tuning and evaluation on larger historical datasets
- 📊 SHAP-based prediction explanations

## 🎯 Project Vision

Most train applications focus on **where a train is and whether it is currently late**.

SmartTrain aims to move toward:

> **"What is the expected ETA at the next station, how might the delay propagate, and what factors are contributing to it?"**

This makes the system a **predictive and explainable ETA platform**, rather than only a train-status display.

## 🔗 Repository

GitHub: https://github.com/VaishnaviKadwad/smarttrain-eta-predictor

---

### Disclaimer

This prototype is based on historical railway data from September 2024. It is not currently a live Indian Railways tracking service. Predictions and disruption simulations are intended for demonstration and research purposes.
