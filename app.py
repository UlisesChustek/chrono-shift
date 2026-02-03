import streamlit as st
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from dateutil import parser
from datetime import datetime

# --- CACHED FUNCTION (API Logic) ---
@st.cache_data(show_spinner=False)
def get_location_data(query):
    """
    Searches for a location and returns the Timezone and Full Address.
    Cached to prevent API rate limiting.
    """
    try:
        geolocator = Nominatim(user_agent="chrono_shift_project_v1")
        location = geolocator.geocode(query, timeout=10)
        
        if location:
            tf = TimezoneFinder()
            detected_timezone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            return detected_timezone, location.address
        return None, None
    except Exception as e:
        return None, None

# --- UI SETUP ---
st.set_page_config(page_title="ChronoShift", page_icon="⏳")
st.title("ChronoShift ⏳")
st.caption("Instantly convert any local time to UTC.")

# --- 1. DATE INPUT ---
# We place this first. As soon as you paste, the app reruns.
col_input, col_result = st.columns([1, 1])

with col_input:
    date_input_str = st.text_input(
        "1. Paste Date & Time:", 
        placeholder="e.g. 2026-02-03 14:30 or Oct 7 5pm",
        help="Accepts almost any format."
    )

# --- 2. TIMEZONE SELECTION (Auto-syncs) ---
st.subheader("2. Source Location / Timezone")

# Initialize default to something distinct (Not UTC)
if 'selected_timezone' not in st.session_state:
    st.session_state['selected_timezone'] = 'America/New_York'

# Optional Location Search
with st.expander("📍 Search by City or Address (Auto-updates Timezone)", expanded=True):
    col_search_1, col_search_2 = st.columns([3, 1])
    
    with col_search_1:
        location_input = st.text_input(
            "Location search:", 
            placeholder="Type city (e.g. London) and press Enter",
            label_visibility="collapsed"
        )
    
    with col_search_2:
        search_btn = st.button("Find Zone", use_container_width=True)

    # Logic: If user searches, we update the session_state immediately
    if (search_btn or location_input) and location_input:
        with st.spinner(f"Locating '{location_input}'..."):
            detected_tz, full_address = get_location_data(location_input)
            if detected_tz:
                st.session_state['selected_timezone'] = detected_tz
                st.success(f"✅ Set to: **{detected_tz}** ({full_address})")
            else:
                st.error("❌ Location not found.")

# Manual Selector (Always visible, stays in sync)
all_timezones = pytz.all_timezones
try:
    current_index = all_timezones.index(st.session_state['selected_timezone'])
except ValueError:
    current_index = 0

selected_tz_name = st.selectbox(
    "Current Timezone Region:",
    all_timezones,
    index=current_index,
    key='manual_timezone_selector',
    on_change=lambda: st.session_state.update({'selected_timezone': st.session_state.manual_timezone_selector})
)

# --- 3. INSTANT CALCULATION ---
# We calculate and display the result immediately (no button needed)

if date_input_str:
    try:
        # 1. Parse the string loosely (handles most formats)
        dt_naive = parser.parse(date_input_str)
        
        # 2. Attach the source timezone
        source_tz = pytz.timezone(selected_tz_name)
        dt_aware = source_tz.localize(dt_naive)
        
        # 3. Convert to UTC
        dt_utc = dt_aware.astimezone(pytz.UTC)
        
        # 4. Display Result
        # We use st.code because it provides a one-click copy button
        st.write("---")
        st.subheader("✅ Converted to UTC:")
        st.code(dt_utc.strftime('%Y-%m-%d %H:%M:%S'), language="text")
        
        # Optional: Show debug info nicely
        st.caption(f"Converted from: {dt_aware.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    except Exception as e:
        st.warning("⚠️ Waiting for a valid date format...")
else:
    # Placeholder state
    st.info("👈 Paste a date above to see the UTC result instantly.")