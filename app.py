import streamlit as st
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from dateutil import parser
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="ChronoShift", page_icon="⏳", layout="centered")

# --- LOGIC: GEO & STATE MANAGER ---
@st.cache_data(show_spinner=False)
def get_timezone_from_string(query):
    """Returns (Timezone_Name, Full_Address) or (None, None)"""
    try:
        geolocator = Nominatim(user_agent="chrono_shift_project_v2")
        location = geolocator.geocode(query, timeout=5)
        if location:
            tf = TimezoneFinder()
            return tf.timezone_at(lng=location.longitude, lat=location.latitude), location.address
        return None, None
    except:
        return None, None

def update_timezone_callback():
    """
    This function runs ONLY when the user hits Enter on the location field.
    It forces the Dropdown to update immediately.
    """
    query = st.session_state.loc_input # Read the input
    if query:
        detected_tz, full_addr = get_timezone_from_string(query)
        if detected_tz:
            # FORCE UPDATE: We write directly to the selectbox's key
            st.session_state.manual_timezone_selector = detected_tz
            st.toast(f"📍 Updated to: {full_addr}", icon="✅")
        else:
            st.toast("❌ Location not found", icon="⚠️")

# --- UI HEADER ---
st.title("ChronoShift ⏳")

# --- 1. DATE INPUT ---
date_input_str = st.text_input(
    "Date & Time", 
    placeholder="Paste here (e.g., Oct 7 5pm, 2026-02-03 14:30)",
    help="Accepts almost any format.",
    key="date_input"
)

# --- 2. LOCATION & TIMEZONE (Synced) ---
col_loc, col_tz = st.columns([1, 1])

# Initialize default if needed
# Default initialization removed to keep fields blank on reset

with col_loc:
    # INPUT: Location
    # 'on_change' ensures the search happens immediately upon Enter
    st.text_input(
        "City / Location (Optional)", 
        placeholder="e.g. Wolf Street 123 / London / Empire state",
        key="loc_input",
        on_change=update_timezone_callback 
    )

with col_tz:
    # INPUT: Selector
    # Note: We don't need 'index=' logic anymore because we are controlling the key directly
    all_timezones = pytz.all_timezones
    
    st.selectbox(
        "Timezone Region",
        all_timezones,
        index=None,
        placeholder="Select timezone...",
        key='manual_timezone_selector' # This key is updated by the callback above
    )

# --- 3. INSTANT RESULT ---
if date_input_str:
    try:
        # Parse & Convert
        dt_naive = parser.parse(date_input_str)
        
        # Get the CURRENT value of the selector (which might have just been auto-updated)
        current_tz_name = st.session_state.manual_timezone_selector
        
        if not current_tz_name:
            st.info("Please select a timezone to proceed.")
            st.stop()

        source_tz = pytz.timezone(current_tz_name)
        
        dt_aware = source_tz.localize(dt_naive)
        dt_utc = dt_aware.astimezone(pytz.UTC)
        
        # Display
        st.write("---")
        st.subheader("UTC Conversion:")
        st.code(dt_utc.strftime('%Y-%m-%d %H:%M:%S'), language="text")
        
        # Calculate UTC offset
        z = dt_aware.strftime('%z') # e.g., +0530, -0300
        sign = z[0]
        hours = int(z[1:3])
        minutes = int(z[3:5])
        
        if minutes == 0 and hours == 0:
            offset_str = "UTC"
        elif minutes == 0:
            offset_str = f"UTC{sign}{hours}"
        else:
            offset_str = f"UTC{sign}{hours}:{minutes:02d}"
            
        st.caption(f"Converted from: {current_tz_name} ({offset_str})")
        
    except Exception:
        st.caption("Waiting for a valid date format...")

# --- 4. FOOTER / CONTROLS ---
st.write("---")
# Custom CSS for minimalist button
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: transparent;
    color: #888;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 0.2rem 1rem;
    font-size: 0.8rem;
    transition: all 0.3s ease;
}
div.stButton > button:first-child:hover {
    color: #333;
    border-color: #333;
    background-color: #f0f0f0;
}
</style>
""", unsafe_allow_html=True)

if st.button("↺ Reset App"):
    # Clear all session state keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()