import streamlit as st
import pandas as pd

# ---------------- LOAD DATA ---------------- #
swap = pd.read_csv("greenkwh.swaps.csv")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
batteries = pd.read_csv("greenkwh.batteries.csv")

# ---------------- CLEAN ---------------- #
swap['serialnumber'] = swap['serialnumber'].astype(str).str.strip().str.upper()
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
batteries['serialnumber'] = batteries['serialnumber'].astype(str).str.strip().str.upper()

swap['created_at'] = pd.to_datetime(swap['created_at'], errors='coerce')

# ---------------- HANDLE COLUMN ISSUES ---------------- #
# Fix mileage spelling
if 'mileage' in energy.columns:
    energy['milage'] = energy['mileage']

# Ensure required columns exist
for col in ['energy_change', 'milage', 'system_type']:
    if col not in energy.columns:
        energy[col] = None

# ---------------- UI ---------------- #
st.set_page_config(layout="wide")
st.title("🔋 Battery Journey Dashboard")

col1, col2 = st.columns([1, 3])

# ---------------- LEFT PANEL ---------------- #
with col1:
    st.subheader("Batteries")
    battery_list = batteries['serialnumber'].dropna().unique()
    selected_battery = st.selectbox("Select Battery", battery_list)

# ---------------- RIGHT PANEL ---------------- #
with col2:
    st.subheader("Battery Journey")

    if selected_battery:

        # ---------------- FILTER ---------------- #
        swap_f = swap[swap['serialnumber'] == selected_battery].copy()
        energy_f = energy[energy['serial_number'] == selected_battery].copy()

        # ---------------- MERGE (SWAP = MAIN) ---------------- #
        df = swap_f.merge(
            energy_f[['serial_number', 'energy_change', 'milage', 'system_type']],
            left_on='serialnumber',
            right_on='serial_number',
            how='left'
        )

        # ---------------- DATE FIX ---------------- #
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df = df.dropna(subset=['created_at'])

        # 🔥 OLDEST → LATEST (as you wanted)
        df = df.sort_values('created_at', ascending=True).reset_index(drop=True)

        # ---------------- STATUS FUNCTION ---------------- #
        def get_status(x, system_type):
            system_type = str(system_type).lower()

            # No charging at consumer
            if system_type == "consumer":
                return "⚡ Discharged"

            if x == 1:
                return "🔌 Charged"
            elif x == 0:
                return "⚡ Discharged"
            else:
                return "⏸️ Idle"

        # ---------------- TIMELINE ---------------- #
        for _, row in df.iterrows():

            # Status
            status = get_status(row.get('setchargingstatus'), row.get('system_type'))

            # Energy
            energy_val = row.get('energy_change')
            energy_kwh = "NA" if pd.isna(energy_val) else f"{energy_val} kWh"

            # Location
            location = row.get('system_type')
            location = "Consumer" if pd.isna(location) else str(location).capitalize()

            # Date
            date = row['created_at'].strftime("%d %b %Y, %I:%M %p")

            st.markdown("---")

            text = f"""
            **{status} {energy_kwh} at {location}**  
            📅 {date}
            """

            # Mileage (only consumer)
            if str(location).lower() == 'consumer':
                mileage = row.get('milage')
                mileage_text = "NA" if pd.isna(mileage) or mileage == 0 else f"{mileage} km"
                text += f"\n🚗 Mileage: {mileage_text}"

            st.markdown(text)