import streamlit as st
import pandas as pd

# ---------------- LOAD ---------------- #
energy = pd.read_csv("greenkwh.energy_sessions.csv")
batteries = pd.read_csv("greenkwh.batteries.csv")
systems = pd.read_csv("greenkwh.systems.csv")

# ---------------- CLEAN ---------------- #
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
batteries['serialnumber'] = batteries['serialnumber'].astype(str).str.strip().str.upper()

systems['user_id'] = systems['user_id'].astype(str).str.strip()
systems['user_name'] = systems['user_name'].astype(str).str.strip()

user_map = dict(zip(systems['user_id'], systems['user_name']))

# ---------------- AUTO DATE COLUMN ---------------- #
date_col = None
for col in ['created_at', 'timestamp', 'time', 'createdat']:
    if col in energy.columns:
        date_col = col
        break

if date_col is None:
    st.error("No datetime column found")
    st.stop()

energy['created_at'] = pd.to_datetime(energy[date_col], errors='coerce')

# ---------------- NORMALIZE ---------------- #
energy['system_type'] = energy['system_type'].astype(str).str.lower().str.strip()

# mileage fix
if 'mileage' in energy.columns:
    energy['milage'] = pd.to_numeric(energy['mileage'], errors='coerce')
else:
    energy['milage'] = None

# 🔥 IMPORTANT FIX → REMOVE NEGATIVE SIGN
energy['energy_change'] = pd.to_numeric(energy['energy_change'], errors='coerce')
energy['energy_change'] = energy['energy_change'].abs()

# remove noise (optional but recommended)
energy = energy[energy['energy_change'] > 0.05]

# ---------------- UI ---------------- #
st.set_page_config(layout="wide")
st.title("🔋 Battery Journey Dashboard")

col1, col2 = st.columns([1, 3])

with col1:
    battery_list = batteries['serialnumber'].dropna().unique()
    selected_battery = st.selectbox("Select Battery", battery_list)

with col2:
    st.subheader("Battery Journey")

    if selected_battery:

        # 🔥 robust filter (fix mismatch issues)
        df = energy[
            energy['serial_number'].str.strip().str.upper() ==
            str(selected_battery).strip().upper()
        ].copy()

        df = df[df['system_type'].isin(['producer', 'consumer'])]
        df = df[df['energy_change'].notna()]
        df = df.dropna(subset=['created_at'])

        if df.empty:
            st.warning("No data for this battery")
            st.stop()

        df = df.sort_values('created_at').reset_index(drop=True)

        df['user_id'] = df['user_id'].astype(str).str.strip()
        df['user_name'] = df['user_id'].map(user_map).fillna("Unknown")

        # ================= SUMMARY ================= #
        total_charged = df[df['system_type'] == 'producer']['energy_change'].sum()
        total_discharged = df[df['system_type'] == 'consumer']['energy_change'].sum()

        total_mileage = df['milage'].sum()
        total_mileage_text = "NA" if pd.isna(total_mileage) or total_mileage == 0 else f"{round(total_mileage,2)} km"

        total_co2_offset = round(total_discharged * 0.6, 2)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("🔌 Total Charged", f"{round(total_charged,2)} GreenKWh")
        c2.metric("⚡ Total Discharged", f"{round(total_discharged,2)} GreenKWh")
        c3.metric("🚗 Total Mileage", total_mileage_text)
        c4.metric("🌱 CO2 Offset", f"{total_co2_offset} kg offset")

        # ---------------- GROUPING ---------------- #
        groups = []
        current_group = []

        for _, row in df.iterrows():

            if not current_group:
                current_group.append(row)
                continue

            last = current_group[-1]

            if (
                row['user_name'] == last['user_name'] and
                row['system_type'] == last['system_type']
            ):
                current_group.append(row)
            else:
                groups.append(pd.DataFrame(current_group))
                current_group = [row]

        if current_group:
            groups.append(pd.DataFrame(current_group))

        groups = groups[::-1]

        # ---------------- DISPLAY ---------------- #
        for g in groups:

            user_name = g['user_name'].iloc[0]
            system_type = g['system_type'].iloc[0]

            # 🔥 SAFE SUM (always positive now)
            total_energy = round(g['energy_change'].sum(), 3)

            start_dt = g['created_at'].min()
            end_dt = g['created_at'].max()

            start_date = start_dt.strftime("%d %b %Y, %I:%M %p")
            end_date = end_dt.strftime("%d %b %Y, %I:%M %p")

            if start_dt == end_dt:
                date_text = f"📅 {start_date}"
            else:
                date_text = f"📅 {start_date} to {end_date}"

            total_mileage = g['milage'].sum()
            mileage_text = "NA" if pd.isna(total_mileage) or total_mileage == 0 else f"{round(total_mileage,2)} km"

            co2_offset = round(total_energy * 0.6, 2)

            if system_type == 'producer':
                status = "🔌 Charged"
                location = f"Producer : {user_name}"
            else:
                status = "⚡ Discharged"
                location = f"Consumer : {user_name}"

            st.markdown("---")

            text = f"""
            **{status} {total_energy} GreenKWh at {location}**  
            {date_text}
            """

            if system_type == 'consumer':
                text += f"\n🚗 Mileage: {mileage_text}"
                text += f"\n🌱 CO2 Offset: {co2_offset} kg"

            st.markdown(text)