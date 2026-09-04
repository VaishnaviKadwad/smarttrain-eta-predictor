
import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(
    page_title="SmartTrain ETA Predictor",
    page_icon="🚆",
    layout="wide"
)

DATA_PATH = "final_dashboard_data.parquet"
BASELINE_MAE = 16.34

@st.cache_resource
def get_connection():
    return duckdb.connect()

con = get_connection()

@st.cache_data
def get_trains():
    return con.execute(f"""
        SELECT DISTINCT train
        FROM read_parquet('{DATA_PATH}')
        WHERE train IS NOT NULL
        ORDER BY train
    """).df()["train"].astype(str).tolist()

@st.cache_data
def get_dates(train):
    result = con.execute(f"""
        SELECT DISTINCT CAST(date AS DATE) AS date
        FROM read_parquet('{DATA_PATH}')
        WHERE CAST(train AS VARCHAR) = ?
        ORDER BY date
    """, [train]).df()

    return result["date"].astype(str).tolist()

@st.cache_data
def get_stations(train, date):
    return con.execute(f"""
        SELECT DISTINCT station
        FROM read_parquet('{DATA_PATH}')
        WHERE CAST(train AS VARCHAR) = ?
          AND CAST(date AS DATE) = CAST(? AS DATE)
          AND station IS NOT NULL
        ORDER BY station
    """, [train, date]).df()["station"].tolist()

@st.cache_data
def get_station_record(train, date, station):
    query = f"""
        SELECT
            train,
            date,
            station,
            sch_arr,
            act_arr,
            arr_delay,
            delay_minutes,
            current_delay,
            previous_station,
            distance_from_previous,
            historical_section_time,
            temperature_c,
            rainfall_mm,
            visibility_m,
            hour,
            day_of_week,
            congestion_score,
            scheduled_datetime,
            predicted_arrival
        FROM read_parquet('{DATA_PATH}')
        WHERE CAST(train AS VARCHAR) = ?
          AND CAST(date AS DATE) = CAST(? AS DATE)
          AND station = ?
        LIMIT 1
    """

    return con.execute(
        query,
        [train, date, station]
    ).df()

st.title("🚆 SmartTrain ETA Predictor")

st.markdown(
    """
    **AI-assisted railway delay prediction and disruption simulation**

    Select a train, journey date and station to estimate arrival time,
    understand the major delay factor and simulate disruptions.
    """
)

st.divider()

st.sidebar.header("Journey Selection")

trains = get_trains()

if not trains:
    st.error("No train data available.")
    st.stop()

selected_train = st.sidebar.selectbox(
    "🚆 Select Train",
    trains
)

dates = get_dates(selected_train)

if not dates:
    st.error("No journey dates available for this train.")
    st.stop()

selected_date = st.sidebar.selectbox(
    "📅 Select Journey Date",
    dates
)

stations = get_stations(
    selected_train,
    selected_date
)

if not stations:
    st.error("No stations available for this journey.")
    st.stop()

selected_station = st.sidebar.selectbox(
    "📍 Select Station",
    stations
)

result = get_station_record(
    selected_train,
    selected_date,
    selected_station
)

if result.empty:
    st.error("No data found for the selected journey.")
    st.stop()

row = result.iloc[0]

scheduled_time = pd.to_datetime(
    row["scheduled_datetime"],
    errors="coerce"
)

predicted_time = pd.to_datetime(
    row["predicted_arrival"],
    errors="coerce"
)

current_delay = row["current_delay"]
actual_delay = row["delay_minutes"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Train", str(selected_train))

with col2:
    st.metric("Station", str(selected_station))

with col3:
    st.metric(
        "Scheduled Arrival",
        scheduled_time.strftime("%I:%M %p")
        if pd.notna(scheduled_time)
        else "N/A"
    )

with col4:
    st.metric(
        "Predicted ETA",
        predicted_time.strftime("%I:%M %p")
        if pd.notna(predicted_time)
        else "N/A"
    )

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("🔮 ETA Prediction")

    if pd.notna(predicted_time):

        lower_time = predicted_time - pd.Timedelta(
            minutes=BASELINE_MAE
        )

        upper_time = predicted_time + pd.Timedelta(
            minutes=BASELINE_MAE
        )

        st.success(
            f"Predicted arrival: "
            f"**{predicted_time.strftime('%I:%M %p')}**"
        )

        st.info(
            f"Typical error: **±{BASELINE_MAE:.2f} minutes**"
        )

        st.write(
            f"Expected range: "
            f"**{lower_time.strftime('%I:%M %p')} – "
            f"{upper_time.strftime('%I:%M %p')}**"
        )

        st.caption(
            "The ±16.34 minute range represents the empirical "
            "baseline MAE, not a statistical confidence interval."
        )

with right:
    st.subheader("📊 Journey Status")

    if pd.notna(current_delay):
        st.write(
            f"Previous-station delay: "
            f"**{current_delay:.1f} minutes**"
        )
    else:
        st.write(
            "Previous-station delay: **Not available**"
        )

    if pd.notna(row["congestion_score"]):
        st.write(
            f"Congestion score: "
            f"**{row['congestion_score']:.2f}**"
        )

    if pd.notna(row["distance_from_previous"]):
        st.write(
            f"Distance from previous station: "
            f"**{row['distance_from_previous']:.1f} km**"
        )

    if pd.notna(row["historical_section_time"]):
        st.write(
            f"Section travel time: "
            f"**{row['historical_section_time']:.1f} min**"
        )

st.divider()

st.subheader("💡 Top Reason for Delay")

reasons = {}

if pd.notna(current_delay) and current_delay > 0:
    reasons["Previous station delay"] = float(current_delay)

if pd.notna(row["congestion_score"]):
    reasons["Railway congestion"] = (
        float(row["congestion_score"]) * 30
    )

if pd.notna(row["rainfall_mm"]) and row["rainfall_mm"] > 0:
    reasons["Rainfall"] = float(row["rainfall_mm"])

if pd.notna(row["visibility_m"]):
    visibility = float(row["visibility_m"])

    if visibility < 5000:
        reasons["Low visibility"] = (
            (5000 - visibility) / 1000
        )

if reasons:
    top_reason = max(
        reasons,
        key=reasons.get
    )

    st.warning(
        f"**Top contributing factor: {top_reason}**"
    )
else:
    st.success(
        "No major contributing factor detected."
    )

st.subheader("📈 Journey Factors")

factor_data = pd.DataFrame({
    "Factor": [
        "Previous Delay",
        "Congestion Score",
        "Distance from Previous",
        "Section Travel Time",
        "Rainfall",
        "Temperature",
        "Visibility"
    ],
    "Value": [
        row["current_delay"],
        row["congestion_score"],
        row["distance_from_previous"],
        row["historical_section_time"],
        row["rainfall_mm"],
        row["temperature_c"],
        row["visibility_m"]
    ]
})

st.dataframe(
    factor_data,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("🌫️ Disruption Simulation")

st.write(
    "Simulate reduced visibility caused by fog "
    "and observe its potential effect on ETA."
)

fog_enabled = st.checkbox(
    "Simulate fog disruption"
)

if fog_enabled:

    fog_visibility = st.slider(
        "Simulated visibility (meters)",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )

    fog_delay = max(
        0,
        (5000 - fog_visibility) / 250
    )

    simulated_eta = (
        predicted_time
        + pd.Timedelta(minutes=fog_delay)
    )

    st.warning(
        f"🌫️ Simulated fog delay: "
        f"**+{fog_delay:.1f} minutes**"
    )

    st.error(
        f"Simulated ETA: "
        f"**{simulated_eta.strftime('%I:%M %p')}**"
    )

    st.caption(
        "Fog simulation is a what-if scenario and is not "
        "part of the verified baseline MAE calculation."
    )

if pd.notna(actual_delay):

    st.divider()

    st.subheader("📌 Historical Validation")

    st.write(
        f"Recorded arrival delay: "
        f"**{actual_delay:.1f} minutes**"
    )

st.divider()

st.caption(
    "SmartTrain ETA Predictor | Railway Delay Prediction Project"
)
