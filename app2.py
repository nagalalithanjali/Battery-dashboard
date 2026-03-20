import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------- CSS ---------------- #
st.markdown("""
<style>
.center-box {
    width: 55%;
    margin: auto;
    font-size: 14px;
    line-height: 1.6;
}
.entry {
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🔋 Battery Journey (Compact View)")

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

# ---------------- DATE ---------------- #
date_col = next((c for c in ['created_at','timestamp','time','createdat'] if c in energy.columns), None)

if not date_col:
    st.error("No datetime column found")
    st.stop()

energy['created_at'] = pd.to_datetime(energy[date_col], errors='coerce')

energy['system_type'] = energy['system_type'].astype(str).str.lower().str.strip()

if 'mileage' in energy.columns:
    energy['milage'] = energy['mileage']

# ---------------- SELECT ---------------- #
battery_list = batteries['serialnumber'].dropna().unique()
selected_battery = st.selectbox("Select Battery", battery_list)

if selected_battery:

    df = energy[energy['serial_number'] == selected_battery].copy()
    df = df[df['system_type'].isin(['producer', 'consumer'])]
    df = df[df['energy_change'].notna()]
    df = df[df['energy_change'] > 0]
    df = df.dropna(subset=['created_at'])

    df = df.sort_values('created_at').reset_index(drop=True)

    df['user_id'] = df['user_id'].astype(str).str.strip()
    df['user_name'] = df['user_id'].map(user_map)

    # ---------------- GROUP ---------------- #
    groups = []
    current_group = []

    for _, row in df.iterrows():

        if not current_group:
            current_group.append(row)
            continue

        last = current_group[-1]

        if row['user_name'] == last['user_name'] and row['system_type'] == last['system_type']:
            current_group.append(row)
        else:
            groups.append(pd.DataFrame(current_group))
            current_group = [row]

    if current_group:
        groups.append(pd.DataFrame(current_group))

    # ---------------- DISPLAY ---------------- #
    st.markdown('<div class="center-box">', unsafe_allow_html=True)

    for i, g in enumerate(groups):

        user_name = g['user_name'].iloc[0]
        system_type = g['system_type'].iloc[0]

        total_energy = round(g['energy_change'].sum(), 3)

        start_dt = g['created_at'].min()
        end_dt = g['created_at'].max()

        start_date = start_dt.strftime("%d %b %Y, %I:%M %p")
        end_date = end_dt.strftime("%d %b %Y, %I:%M %p")

        date_text = start_date if start_dt == end_dt else f"{start_date} → {end_date}"

        total_mileage = g['milage'].sum() if 'milage' in g.columns else 0
        mileage_text = "" if pd.isna(total_mileage) or total_mileage == 0 else f" — 🚗 {round(total_mileage,2)} km"

        status = "🔌 Charged" if system_type == 'producer' else "⚡ Discharged"

        # indentation for alternate
        indent = "&nbsp;" * 10 if i % 2 != 0 else ""

        line = f"""
        <div class="entry">
        {indent}{status} ({user_name}) — {total_energy} GreenkWh — 📅 {date_text}{mileage_text}
        </div>
        """

        st.markdown(line, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)