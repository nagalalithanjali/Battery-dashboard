import streamlit as st
import pandas as pd

# ---------------- CONSTANTS ---------------- #
MAX_BATTERY_KWH = 2.3
CO2_PER_KWH = 0.06  # used with mileage now
PRICE_PER_KWH = 16
PETROL_PER_LITRE = 107.5
SWAP_COST = 80

# ---------------- PAGE ---------------- #
st.set_page_config(layout="wide")

# ---------------- UI STYLE ---------------- #
st.markdown("""
""", unsafe_allow_html=True)

st.title("📊 User Energy Dashboard")

# ---------------- LOAD ---------------- #
users = pd.read_json("greenkwh.users.json")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
systems = pd.read_csv("greenkwh.systems.csv")

# ---------------- CLEAN ---------------- #
users['id'] = users['id'].astype(str).str.strip()
users['name'] = users['name'].astype(str).str.strip()

energy['user_id'] = energy['user_id'].astype(str).str.strip()
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
energy['connected_system'] = energy['connected_system'].astype(str).str.strip()
energy['timestamp'] = pd.to_datetime(energy['timestamp'], errors='coerce', utc=True).dt.tz_convert('Asia/Kolkata')
energy['disconnected_time'] = pd.to_datetime(energy['disconnected_time'], errors='coerce', utc=True).dt.tz_convert('Asia/Kolkata')
energy['energy_change'] = pd.to_numeric(energy['energy_change'], errors='coerce').abs()
energy['mileage'] = pd.to_numeric(energy['mileage'], errors='coerce').fillna(0)
energy['system_type'] = energy['system_type'].str.lower().str.strip()

systems['user_id'] = systems['user_id'].astype(str).str.strip()
systems['system_serial'] = systems['system_serial'].astype(str).str.strip()
systems['system_type'] = systems['system_type'].str.lower().str.strip()

# ---------------- MAP ---------------- #
id_to_name = dict(zip(users['id'], users['name']))
name_to_id = dict(zip(users['name'], users['id']))

# ---------------- SIDEBAR ---------------- #
summary = energy.groupby(['user_id', 'system_type'])['energy_change'].sum().unstack(fill_value=0)
summary['category'] = summary.apply(
    lambda x: 'both' if x.get('producer', 0) > 0 and x.get('consumer', 0) > 0
    else 'producer' if x.get('producer', 0) > 0
    else 'consumer',
    axis=1
)

category = st.sidebar.selectbox("Select Type", ["producer", "consumer", "both"])
filtered_ids = summary[summary['category'] == category].index
filtered_names = [id_to_name[i] for i in filtered_ids if i in id_to_name]
selected_user = st.sidebar.selectbox("Select User", filtered_names)

# ---------------- DATA ---------------- #
uid = name_to_id[selected_user]
df = energy[energy['user_id'] == uid].copy()
df = df[df['system_type'].isin(['producer', 'consumer'])]
df = df.dropna(subset=['timestamp'])

# Sort by timestamp so consecutive rows are in order
df = df.sort_values('timestamp').reset_index(drop=True)

# ---------------- SESSION GROUPING ---------------- #
# A new session starts whenever serial_number OR connected_system changes.
# We detect this by comparing each row to the previous row.
# This correctly splits sessions even if the same battery+system pair
# appears again later after being disconnected in between.

# ---------------- SESSION GROUPING ---------------- #
# Walk all rows sorted by timestamp (global timeline).
# A new session starts when serial_number OR connected_system changes,
# OR when there is a real gap (> 2 min) between the previous row's
# disconnected_time and the current row's timestamp for the SAME battery+system.
# If Battery A → Battery B → Battery A appears, the second Battery A
# is a new session because something changed in between on the timeline.

def build_sessions(df):
    if df.empty:
        return pd.DataFrame()

    sessions = []
    session_rows = []
    prev_key = None
    prev_disconnected = None

    for _, row in df.iterrows():
        curr_key = (row['serial_number'], row['connected_system'], row['system_type'])
        curr_start = row['timestamp']

        new_session = False
        if prev_key is None:
            new_session = True
        elif curr_key != prev_key:
            # Different battery or system → new session
            new_session = True
        else:
            # Same battery+system: split only on a real gap (> 2 min)
            # The 2-min tolerance handles normal midnight splits (18:29 → 18:30)
            gap = (curr_start - prev_disconnected).total_seconds()
            if gap > 120:
                new_session = True

        if new_session and session_rows:
            sessions.append(_aggregate_session(session_rows))
            session_rows = []

        session_rows.append(row)
        prev_key = curr_key
        prev_disconnected = row['disconnected_time'] if pd.notna(row['disconnected_time']) else row['timestamp']

    if session_rows:
        sessions.append(_aggregate_session(session_rows))

    return pd.DataFrame(sessions)


def _aggregate_session(rows):
    first = rows[0]
    last = rows[-1]
    total_energy = sum(r['energy_change'] for r in rows if pd.notna(r['energy_change']))
    total_mileage = sum(r['mileage'] for r in rows if pd.notna(r['mileage']))
    start_time = first['timestamp']
    end_time = last['disconnected_time'] if pd.notna(last['disconnected_time']) else last['timestamp']
    return {
        'system_type': first['system_type'],
        'battery': first['serial_number'],       # serial_number = battery
        'system': first['connected_system'],     # connected_system = system
        'energy': total_energy,
        'mileage': total_mileage,
        'start': start_time,
        'end': end_time,
        'sessions': len(rows),
    }


grouped = build_sessions(df)

# ---------------- MONEY SAVED ---------------- #
def calc_money_saved(mileage):
    if pd.isna(mileage) or mileage == 0:
        return 0
    petrol_cost = (mileage / 40) * PETROL_PER_LITRE
    return max(petrol_cost - SWAP_COST, 0)

if not grouped.empty:
    grouped['money'] = grouped['mileage'].apply(calc_money_saved)
else:
    grouped['money'] = []

producer_data = grouped[grouped['system_type'] == 'producer'] if not grouped.empty else pd.DataFrame()
consumer_data = grouped[grouped['system_type'] == 'consumer'] if not grouped.empty else pd.DataFrame()

total_produced = producer_data['energy'].sum() if not producer_data.empty else 0
total_consumed = consumer_data['energy'].sum() if not consumer_data.empty else 0
total_saved = consumer_data['money'].sum() if not consumer_data.empty else 0
total_earned = total_produced * PRICE_PER_KWH
total_sessions = grouped['sessions'].sum() if not grouped.empty else 0
total_mileage = consumer_data['mileage'].sum() if not consumer_data.empty else 0
total_co2 = total_mileage * CO2_PER_KWH

# ---------------- SUMMARY ---------------- #
st.markdown("### 🚀 Energy Impact Summary")

def metric_box(icon, label, value):
    return f"""
<div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:14px 18px; text-align:left; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
  <div style="font-size:12px; color:#6b7280; margin-bottom:4px;">{icon} {label}</div>
  <div style="font-size:18px; font-weight:700; color:#111827;">{value}</div>
</div>"""

if category == "producer":
    boxes = (
        metric_box("🔋", "Energy Produced", f"{round(total_produced, 2)} GreenKWh") +
        metric_box("🔢", "Total Sessions", int(total_sessions)) +
        metric_box("💰", "Money Earned", f"₹{round(total_earned, 2)}")
    )
    cols = 3
elif category == "consumer":
    boxes = (
        metric_box("⚡", "Energy Consumed", f"{round(total_consumed, 2)} GreenKWh") +
        metric_box("🔢", "Total Sessions", int(total_sessions)) +
        metric_box("🚗", "Total Mileage", f"{int(total_mileage)} km") +
        metric_box("🌱", "CO₂ Offset", f"{round(total_co2, 2)} kg") +
        metric_box("💰", "Money Saved", f"₹{round(total_saved, 2)}")
    )
    cols = 5
else:
    boxes = (
        metric_box("🔋", "Energy Produced", f"{round(total_produced, 2)} GreenKWh") +
        metric_box("⚡", "Energy Consumed", f"{round(total_consumed, 2)} GreenKWh") +
        metric_box("🔢", "Total Sessions", int(total_sessions)) +
        metric_box("🚗", "Total Mileage", f"{int(total_mileage)} km") +
        metric_box("🌱", "CO₂ Offset", f"{round(total_co2, 2)} kg") +
        metric_box("💰", "Total Savings", f"₹{round(total_saved + total_earned, 2)}")
    )
    cols = 6

st.markdown(
    f'<div style="display:grid; grid-template-columns:repeat({cols}, 1fr); gap:12px; margin-bottom:24px;">{boxes}</div>',
    unsafe_allow_html=True
)

# ---------------- CARDS ---------------- #
if not grouped.empty:
    grouped = grouped.sort_values('start', ascending=False)

    for _, row in grouped.iterrows():
        start = row['start'].strftime("%d %b %Y, %I:%M %p")
        end = row['end'].strftime("%d %b %Y, %I:%M %p")

        if row['system_type'] == 'producer':
            st.markdown(f"""
<div style="border-left: 4px solid #22c55e; background: #f0fdf4; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; font-size: 13px;">
  <p style="margin:3px 0; font-size:14px;">🔋 <b>Produced: {round(row['energy'], 2)} GreenKWh</b></p>
  <p style="margin:3px 0; color:#6b7280;">🆔 System: {row['system']}</p>
  <p style="margin:3px 0; color:#6b7280;">🔋 Battery: {row['battery']}</p>
  <p style="margin:3px 0; color:#6b7280;">📅 {start} → {end}</p>
  <p style="margin:3px 0;">💰 <b>Money Earned: ₹{round(row['energy'] * PRICE_PER_KWH, 2)}</b></p>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div style="border-left: 4px solid #f97316; background: #fff7ed; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; font-size: 13px;">
  <p style="margin:3px 0; font-size:14px;">⚡ <b>Consumed: {round(row['energy'], 2)} GreenKWh</b></p>
  <p style="margin:3px 0; color:#6b7280;">🆔 System: {row['system']}</p>
  <p style="margin:3px 0; color:#6b7280;">🔋 Battery: {row['battery']}</p>
  <p style="margin:3px 0; color:#6b7280;">📅 {start} → {end}</p>
  <p style="margin:3px 0; color:#6b7280;">🚗 Mileage: {int(row['mileage'])} km</p>
  <p style="margin:3px 0; color:#6b7280;">🌱 CO₂ Offset: {round(row['mileage'] * CO2_PER_KWH, 2)} kg</p>
  <p style="margin:3px 0;">💰 <b>Money Saved: ₹{round(row['money'], 2)}</b></p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)