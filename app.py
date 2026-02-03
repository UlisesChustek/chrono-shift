import streamlit as st
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

# --- CACHED FUNCTION (API Logic) ---
@st.cache_data(show_spinner=False)
def get_location_data(query):
    """
    Searches for a location and returns the Timezone and Full Address.
    Cached to prevent API rate limiting.
    """
    try:
        # User_agent must be unique to your project
        geolocator = Nominatim(user_agent="chrono_shift_project_v1")
        location = geolocator.geocode(query, timeout=10)
        
        if location:
            tf = TimezoneFinder()
            # Get timezone from coordinates
            detected_timezone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            return detected_timezone, location.address
        return None, None
    except Exception as e:
        return None, None

# --- UI SETUP ---
st.title("ChronoShift ⏳")
st.subheader("Timezone Configuration")

# --- AUTO-DETECTION SECTION ---
with st.expander("🌍 Don't know your timezone? Search by location", expanded=True):
    col_search_1, col_search_2 = st.columns([3, 1])
    
    with col_search_1:
        location_input = st.text_input(
            "Enter City, Country or Address:", 
            placeholder="Ex: New York, Santiago del Estero 118..."
        )
    
    with col_search_2:
        st.write("") # Vertical spacer
        st.write("") 
        search_btn = st.button("Detect Zone")

    # Processing Logic
    if search_btn and location_input:
        with st.spinner(f"Searching for '{location_input}'..."):
            detected_tz, full_address = get_location_data(location_input)
            
            if detected_tz:
                st.success(f"✅ Location found: **{full_address}**")
                st.info(f"⏰ Detected Timezone: **{detected_tz}**")
                
                # UPDATE SESSION STATE
                # This overrides the manual selection
                st.session_state['selected_timezone'] = detected_tz
            else:
                st.error("❌ Location not found. Please try being more specific.")

# --- MANUAL SELECTOR SECTION ---
all_timezones = pytz.all_timezones

# Initialize default state if not present
if 'selected_timezone' not in st.session_state:
    st.session_state['selected_timezone'] = 'UTC'