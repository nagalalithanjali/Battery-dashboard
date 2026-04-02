import streamlit as st
import pandas as pd
import numpy as np
 
st.set_page_config(layout="wide")
 
# ---------------- CSS ---------------- #
st.markdown("""
<style>
.timeline {
    position: relative;
    margin: 30px 0;
}
.timeline::after {
    content: '';
    position: absolute;
    width: 4px;
    background-color: #888;
    top: 0;
    bottom: 0;
    left: 50%;
    margin-left: -2px;
}
.container {
    padding: 15px 40px;
    position: relative;
    width: 50%;
}
.left { left: 0; }
.right { left: 50%; }
.content {
    padding: 15px;
    border-radius: 12px;
    color: white;
    margin-bottom: 10px;
}
.charge { background-color: #065f46; }
.discharge { background-color: #9a3412; }
.placeholder-charge { background-color: #064e3b; opacity: 0.5; border: 2px solid #6ee7b7; }
.placeholder-discharge { background-color: #7c2d12; opacity: 0.5; border: 2px solid #fdba74; }
</style>
""", unsafe_allow_html=True)
 
st.title("🔋 Battery Journey Roadmap")
 
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
    df = df.dropna(subset=['created_at'])
 
    df['energy_change'] = pd.to_numeric(df['energy_change'], errors='coerce')
    df['energy_change'] = df['energy_change'].abs()
 
    df = df.sort_values('created_at', ascending=False).reset_index(drop=True)
 
    df['user_id'] = df['user_id'].astype(str).str.strip()
    df['user_name'] = df['user_id'].map(user_map)
 
    # ================= SUMMARY ================= #
    total_charged = round(df[df['system_type'] == 'producer']['energy_change'].sum(), 2)
    total_discharged = round(df[df['system_type'] == 'consumer']['energy_change'].sum(), 2)
 
    total_mileage = df['milage'].sum() if 'milage' in df.columns else 0
    total_mileage_text = "NA" if pd.isna(total_mileage) or total_mileage == 0 else f"{round(total_mileage, 2)} km"
 
    total_co2_offset = round(total_mileage * 0.06, 2) if total_mileage > 0 else 0.0
 
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔌 Total Charged", f"{total_charged} GreenKWh")
    c2.metric("⚡ Total Discharged", f"{total_discharged} GreenKWh")
    c3.metric("🚗 Total Mileage", total_mileage_text)
    c4.metric("🌱 CO2 Offset", f"{total_co2_offset} kg")
 
    st.markdown("---")
 
    # ---------------- ORIGINAL GROUP LOGIC (unchanged) ---------------- #
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
 
    # ---------------- INSERT DUMMY CARD between consecutive same-type groups ---------------- #
    # Only inserting a visual placeholder — original data/groups are NOT touched
    final_groups = []
 
    for i, g in enumerate(groups):
        final_groups.append(("real", g))
        if i + 1 < len(groups):
            current_type = g['system_type'].iloc[0]
            next_type = groups[i + 1]['system_type'].iloc[0]
            if current_type == next_type:
                opposite = 'consumer' if current_type == 'producer' else 'producer'
                final_groups.append(("placeholder", opposite))
 
    # ---------------- TIMELINE ---------------- #
    timeline_html = '<div class="timeline">'
 
    for item in final_groups:
        kind = item[0]
 
        if kind == "placeholder":
            opposite = item[1]
            if opposite == 'producer':
                timeline_html += """<div class="container left">
<div class="content placeholder-charge">
<b>🔌 Charged NA GreenKWh</b><br>
👤 Site
</div>
</div>"""
            else:
                timeline_html += """<div class="container right">
<div class="content placeholder-discharge">
<b>⚡ Discharged NA GreenKWh</b><br>
👤 Partner
</div>
</div>"""
            continue
 
        # --- real card (original logic untouched) ---
        g = item[1]
        user_name = g['user_name'].iloc[0]
        system_type = g['system_type'].iloc[0]
 
        total_energy = round(g['energy_change'].sum(), 2)
 
        start_dt = g['created_at'].min()
        end_dt = g['created_at'].max()
        start_date = start_dt.strftime("%d %b %Y, %I:%M %p")
        end_date = end_dt.strftime("%d %b %Y, %I:%M %p")
        date_text = start_date if start_dt == end_dt else f"{start_date} → {end_date}"
 
        total_mileage_g = g['milage'].sum() if 'milage' in g.columns else 0
        mileage_text = "NA" if pd.isna(total_mileage_g) or total_mileage_g == 0 else f"{round(total_mileage_g, 2)} km"
        co2_offset = round(total_mileage_g * 0.06, 2) if total_mileage_g > 0 else 0.0
 
        if system_type == 'producer':
            side = "left"
            css_class = "charge"
            status = "🔌 Charged"
            extra_line = ""
        else:
            side = "right"
            css_class = "discharge"
            status = "⚡ Discharged"
            extra_line = f"<br>🚗 Mileage: {mileage_text}<br>🌱 CO2 Offset: {co2_offset} kg"
 
        timeline_html += f"""<div class="container {side}">
<div class="content {css_class}">
<b>{status} {total_energy} GreenKWh</b><br>
👤 {user_name}<br>
📅 {date_text}
{extra_line}
</div>
</div>"""
 
    timeline_html += "</div>"
 
    st.markdown(timeline_html, unsafe_allow_html=True)
 