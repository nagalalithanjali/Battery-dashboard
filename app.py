import streamlit as st
import pandas as pd

# ---------------- LOAD ---------------- #
energy = pd.read_csv("greenkwh.energy_sessions.csv")
batteries = pd.read_csv("greenkwh.batteries.csv")

# ---------------- CLEAN ---------------- #
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
batteries['serialnumber'] = batteries['serialnumber'].astype(str).str.strip().str.upper()

# ---------------- AUTO DATE COLUMN ---------------- #
date_col = None
for col in ['created_at', 'timestamp', 'time', 'createdat']:
    if col in energy.columns:
        date_col = col
        break

if date_col is None:
    st.error("No datetime column found")
    st.write(energy.columns.tolist())
    st.stop()

energy['created_at'] = pd.to_datetime(energy[date_col], errors='coerce')

# ---------------- NORMALIZE ---------------- #
energy['system_type'] = energy['system_type'].astype(str).str.lower().str.strip()

if 'mileage' in energy.columns:
    energy['milage'] = energy['mileage']

# ---------------- UI ---------------- #
st.set_page_config(layout="wide")
st.title("🔋 Battery Journey Dashboard")

col1, col2 = st.columns([1, 3])

# LEFT PANEL
with col1:
    battery_list = batteries['serialnumber'].dropna().unique()
    selected_battery = st.selectbox("Select Battery", battery_list)

# RIGHT PANEL
with col2:
    st.subheader("Battery Journey")

    if selected_battery:

        # ---------------- FILTER ---------------- #
        df = energy[energy['serial_number'] == selected_battery].copy()

        # KEEP ONLY REAL SYSTEMS
        df = df[df['system_type'].isin(['producer', 'consumer'])]

        # REMOVE GARBAGE
        df = df[df['energy_change'].notna()]
        df = df[df['energy_change'] > 0]   # only positive real values

        # REMOVE BAD DATES
        df = df.dropna(subset=['created_at'])

        # SORT (LATEST → OLDEST)
        df = df.sort_values('created_at', ascending=False).reset_index(drop=True)

        # ---------------- DISPLAY ---------------- #
        for _, row in df.iterrows():

            if row['system_type'] == 'producer':
                status = "🔌 Charged"
                location = "Producer"
            else:
                status = "⚡ Discharged"
                location = "Consumer"

            energy_val = round(row['energy_change'], 3)
            date = row['created_at'].strftime("%d %b %Y, %I:%M %p")

            st.markdown("---")

            text = f"""
            **{status} {energy_val} kWh at {location}**  
            📅 {date}
            """

            # mileage only for consumer
            if row['system_type'] == 'consumer':
                mileage = row.get('milage')
                mileage_text = "NA" if pd.isna(mileage) or mileage == 0 else f"{mileage} km"
                text += f"\n🚗 Mileage: {mileage_text}"

            st.markdown(text)