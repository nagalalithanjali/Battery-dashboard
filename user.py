import streamlit as st
import pandas as pd

# ---------------- LOAD ---------------- #
users = pd.read_json("greenkwh.users.json")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
systems = pd.read_csv("greenkwh.systems.csv")

MAX_BATTERY_KWH = 2.3
CO2_PER_KM = 0.07  # kg CO2 per km (petrol equivalent)

# ---------------- CLEAN ---------------- #
users['id'] = users['id'].astype(str).str.strip()
energy['user_id'] = energy['user_id'].astype(str).str.strip()
systems['user_id'] = systems['user_id'].astype(str).str.strip()

users['name'] = users['name'].astype(str).str.strip()

energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
systems['system_serial'] = systems['system_serial'].astype(str).str.strip()

# ✅ USE REAL TIMESTAMP
energy['timestamp'] = pd.to_datetime(energy['timestamp'], errors='coerce', utc=True)
energy['timestamp'] = energy['timestamp'].dt.tz_convert('Asia/Kolkata')

# numeric safety
energy['energy_change'] = pd.to_numeric(energy['energy_change'], errors='coerce')
energy['mileage'] = pd.to_numeric(energy['mileage'], errors='coerce')

# ---------------- MAP ---------------- #
user_map = dict(zip(users['name'], users['id']))

# ---------------- UI ---------------- #
st.set_page_config(layout="wide")
st.title("📊 User Dashboard")

col1, col2 = st.columns([1,3])

with col1:
    selected_user = st.selectbox("Select User", users['name'].dropna().unique())

with col2:

    if selected_user:

        uid = user_map[selected_user]

        # ---------------- FILTER ---------------- #
        df = energy[energy['user_id'] == uid].copy()

        if df.empty:
            st.warning("No data available")
            st.stop()

        # ---------------- VALID TYPES ---------------- #
        df['system_type'] = df['system_type'].str.lower().str.strip()
        df = df[df['system_type'].isin(['producer','consumer'])]

        # ---------------- REMOVE JUNK ---------------- #
        df = df[~((df['energy_change'] == 0) & (df['mileage'] == 0))]
        df = df[df['energy_change'] <= MAX_BATTERY_KWH]

        # ---------------- SYSTEM ---------------- #
        sys_map = systems[systems['user_id'] == uid]
        system_id = sys_map['system_serial'].iloc[0] if not sys_map.empty else "NA"
        df['system_serial'] = system_id

        # ---------------- REMOVE DUPLICATES ---------------- #
        df = df.sort_values('timestamp')
        df = df.drop_duplicates(subset=['serial_number'], keep='last')

        # ================= 🔥 IMPACT METRICS ================= #

        total_produced = df[df['system_type'] == 'producer']['energy_change'].sum()
        total_consumed = df[df['system_type'] == 'consumer']['energy_change'].sum()
        total_mileage = df[df['system_type'] == 'consumer']['mileage'].sum()

        co2_offset = total_mileage * CO2_PER_KM

        st.markdown("### 🚀 Energy Impact Summary")
        st.markdown("---")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("🔋 Energy Produced", f"{round(total_produced,2)} GreenkWh")

        with c2:
            st.metric("⚡ Energy Consumed", f"{round(total_consumed,2)} GreenkWh")

        with c3:
            st.metric("🚗 Mileage", f"{int(total_mileage)} km")

        with c4:
            st.metric("🌱 CO₂ Offset", f"{round(co2_offset,2)} kg")


        # ---------------- SORT ---------------- #
        df = df.sort_values('timestamp', ascending=False)

        # ---------------- DISPLAY ---------------- #
        for _, row in df.iterrows():

            energy_val = round(row['energy_change'], 2)

            if row['system_type'] == 'producer':
                title = f"🔋 Produced {energy_val} GreenkWh"
            else:
                title = f"⚡ Consumed {energy_val} GreenkWh"

            time_text = row['timestamp'].strftime("%d %b %Y, %I:%M %p IST")

            # -------- MILEAGE -------- #
            mileage_text = ""
            if row['system_type'] == 'consumer':
                if pd.isna(row['mileage']) or row['mileage'] == 0:
                    mileage_text = "🚗 Mileage: NA"
                else:
                    mileage_text = f"🚗 Mileage: {int(row['mileage'])} km"

            st.markdown("---")

            if row['system_type'] == 'consumer':
                st.markdown(f"""
                **{title}**  
                🆔 System: {row['system_serial']}  
                🔋 Battery: {row['serial_number']}  
                📅 {time_text}  
                {mileage_text}
                """)
            else:
                st.markdown(f"""
                **{title}**  
                🆔 System: {row['system_serial']}  
                🔋 Battery: {row['serial_number']}  
                📅 {time_text}
                """)