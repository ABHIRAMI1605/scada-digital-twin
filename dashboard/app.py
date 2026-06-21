import pandas as pd
import streamlit as st

CSV_PATH = "data/readings.csv"
ALARMS_CSV_PATH = "data/alarms.csv"
WINDOW = 60

st.set_page_config(page_title="Plant SCADA Dashboard", layout="wide")
st.title("Industrial Power Monitoring — Plant Overview")


@st.fragment(run_every="2s")
def render_dashboard():
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        st.warning("No data yet — start data_logger.py first.")
        return

    if df.empty:
        st.warning("CSV is empty — waiting for first reading.")
        return

    latest = df.iloc[-1]
    recent = df.tail(WINDOW)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Bus Voltage (V)", f"{latest['bus_voltage_v']:.1f}")
    col2.metric("Active Power (kW)", f"{latest['total_kw']:.1f}")
    col3.metric("Reactive Power (kVAR)", f"{latest['total_kvar']:.1f}")
    col4.metric("Power Factor", f"{latest['power_factor']:.3f}")
    col5.metric("Current (A)", f"{latest['current_a']:.1f}")

    st.subheader("Trends")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Bus Voltage")
        st.line_chart(recent.set_index("sim_time_s")[["bus_voltage_v"]])
    with c2:
        st.caption("Real vs Reactive Power")
        st.line_chart(recent.set_index("sim_time_s")[["total_kw", "total_kvar"]])

    st.subheader("Alarm Panel")
    try:
        alarms_df = pd.read_csv(ALARMS_CSV_PATH)
    except FileNotFoundError:
        alarms_df = pd.DataFrame()

    if alarms_df.empty:
        st.success("No active alarms or trips.")
    else:
        recent_alarms = alarms_df.tail(10).iloc[::-1]
        for _, row in recent_alarms.iterrows():
            msg = f"[{row['ansi_code']}] {row['description']} — {row['value']} {row['unit']} ({row['timestamp']})"
            if row["severity"] == "TRIP":
                st.error(msg)
            else:
                st.warning(msg)

    st.caption(f"Last updated: {latest['timestamp']}")


render_dashboard()
