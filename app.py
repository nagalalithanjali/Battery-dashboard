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

if 'mileage' in energy.columns:
    energy['milage'] = energy['mileage']

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

        df = energy[energy['serial_number'] == selected_battery].copy()
        df = df[df['system_type'].isin(['producer', 'consumer'])]
        df = df[df['energy_change'].notna()]
        df = df[df['energy_change'] > 0]
        df = df.dropna(subset=['created_at'])

        # sort oldest → newest (important for grouping)
        df = df.sort_values('created_at').reset_index(drop=True)

        # map user names
        df['user_id'] = df['user_id'].astype(str).str.strip()
        df['user_name'] = df['user_id'].map(user_map)

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

        # show latest first
        groups = groups[::-1]

        # ---------------- DISPLAY ---------------- #
        for g in groups:

            user_name = g['user_name'].iloc[0]
            system_type = g['system_type'].iloc[0]

            total_energy = round(g['energy_change'].sum(), 3)

            start_dt = g['created_at'].min()
            end_dt = g['created_at'].max()

            start_date = start_dt.strftime("%d %b %Y, %I:%M %p")
            end_date = end_dt.strftime("%d %b %Y, %I:%M %p")

            # smart date display
            if start_dt == end_dt:
                date_text = f"📅 {start_date}"
            else:
                date_text = f"📅 {start_date} to {end_date}"

            total_mileage = g['milage'].sum() if 'milage' in g.columns else 0
            mileage_text = "NA" if pd.isna(total_mileage) or total_mileage == 0 else f"{round(total_mileage,2)} km"

            if system_type == 'producer':
                status = "🔌 Charged"
                location = f"Producer : {user_name}"
            else:
                status = "⚡ Discharged"
                location = f"Consumer : {user_name}"

            st.markdown("---")

            text = f"""
            **{status} {total_energy} kWh at {location}**  
            {date_text}
            """

            if system_type == 'consumer':
                text += f"\n🚗 Mileage: {mileage_text}"

            st.markdown(text)