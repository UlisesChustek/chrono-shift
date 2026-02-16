"""
Comprehensive QA Test Suite for ChronoShift Application
========================================================
Senior QA Automation Engineer: Python & Streamlit Testing

This test suite validates:
- Timezone detection logic
- External API mocking (prevents rate limiting)
- Streamlit session state callbacks
- Edge cases and error handling
- Caching behavior
- Security and robustness
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime
import streamlit as st


# ============================================================================
# FIXTURES & MOCKING SETUP
# ============================================================================

@pytest.fixture
def mock_nominatim_location():
    """Mock Nominatim location response"""
    def _create_location(address, lat, lng):
        location = Mock()
        location.address = address
        location.latitude = lat
        location.longitude = lng
        return location
    return _create_location


@pytest.fixture
def mock_geolocator(mock_nominatim_location):
    """Mock geopy Nominatim geolocator"""
    with patch('app.Nominatim') as mock_nom:
        geolocator = Mock()
        mock_nom.return_value = geolocator
        
        # Define common and complex test locations
        location_database = {
            # Standard Cities
            'new york': mock_nominatim_location('New York, NY, USA', 40.7128, -74.0060),
            'london': mock_nominatim_location('London, UK', 51.5074, -0.1278),
            'tokyo': mock_nominatim_location('Tokyo, Japan', 35.6762, 139.6503),
            'sydney': mock_nominatim_location('Sydney, NSW, Australia', -33.8688, 151.2093),
            'são paulo': mock_nominatim_location('São Paulo, Brazil', -23.5505, -46.6333),
            'paris': mock_nominatim_location('Paris, France', 48.8566, 2.3522),
            'paris, texas': mock_nominatim_location('Paris, Texas, USA', 33.6609, -95.5555),
            'zürich': mock_nominatim_location('Zürich, Switzerland', 47.3769, 8.5417),
            'berlin': mock_nominatim_location('Berlin, Germany', 52.5200, 13.4050),
            'moscow': mock_nominatim_location('Moscow, Russia', 55.7558, 37.6173),
            
            # Non-Integer Offsets (30 or 45 min)
            'delhi': mock_nominatim_location('Delhi, India', 28.6139, 77.2090),  # UTC+5:30
            'kathmandu': mock_nominatim_location('Kathmandu, Nepal', 27.7172, 85.3240), # UTC+5:45
            'st. john\'s': mock_nominatim_location('St. John\'s, NL, Canada', 47.5615, -52.7126), # UTC-3:30
            'adelaide': mock_nominatim_location('Adelaide, SA, Australia', -34.9285, 138.6007), # UTC+9:30
            'eucla': mock_nominatim_location('Eucla, WA, Australia', -31.6772, 128.8837), # UTC+8:45
            'chatham islands': mock_nominatim_location('Chatham Islands, NZ', -44.0000, -176.5000), # UTC+12:45
            
            # Date Line & Extreme Zones
            'apia': mock_nominatim_location('Apia, Samoa', -13.8333, -171.7667), # UTC+13
            'kiritimati': mock_nominatim_location('Kiritimati, Kiribati', 1.8721, -157.3632), # UTC+14
            'adak': mock_nominatim_location('Adak, Alaska, USA', 51.8800, -176.6581), # UTC-10 (Aleutian)
            
            # Antarctica & Special Territories
            'mcmurdo station': mock_nominatim_location('McMurdo Station, Antarctica', -77.8460, 166.6680), # Uses NZ time
            'palmer station': mock_nominatim_location('Palmer Station, Antarctica', -64.7742, -64.0531), # Uses Chile time
            'longyearbyen': mock_nominatim_location('Longyearbyen, Svalbard', 78.2232, 15.6267), # Arctic
            
            # Complex DST & Political
            'lord howe island': mock_nominatim_location('Lord Howe Island, Australia', -31.5553, 159.0821), # +10:30 -> +11 (30m DST)
            'simferopol': mock_nominatim_location('Simferopol, Crimea', 44.9572, 34.1108), # Political flux
            'phoenix': mock_nominatim_location('Phoenix, Arizona, USA', 33.4484, -112.0740), # No DST
        }
        
        def geocode_side_effect(query, timeout=None):
            query_lower = query.lower().strip()
            return location_database.get(query_lower, None)
        
        geolocator.geocode.side_effect = geocode_side_effect
        yield geolocator


@pytest.fixture
def mock_timezonefinder():
    """Mock TimezoneFinder"""
    with patch('app.TimezoneFinder') as mock_tf:
        tf_instance = Mock()
        mock_tf.return_value = tf_instance
        
        # Define timezone mappings for coordinates
        timezone_database = {
            # Standard
            (40.7128, -74.0060): 'America/New_York',     
            (51.5074, -0.1278): 'Europe/London',         
            (35.6762, 139.6503): 'Asia/Tokyo',           
            (-33.8688, 151.2093): 'Australia/Sydney',    
            (-23.5505, -46.6333): 'America/Sao_Paulo',   
            (48.8566, 2.3522): 'Europe/Paris',           
            (33.6609, -95.5555): 'America/Chicago',      
            (47.3769, 8.5417): 'Europe/Zurich',          
            (52.5200, 13.4050): 'Europe/Berlin',         
            (55.7558, 37.6173): 'Europe/Moscow',         
            
            # Non-Integer Offsets
            (28.6139, 77.2090): 'Asia/Kolkata',          # Delhi (UTC+5:30)
            (27.7172, 85.3240): 'Asia/Kathmandu',        # Kathmandu (UTC+5:45)
            (47.5615, -52.7126): 'America/St_Johns',     # St. John's (UTC-3:30)
            (-34.9285, 138.6007): 'Australia/Adelaide',  # Adelaide (UTC+9:30)
            (-31.6772, 128.8837): 'Australia/Eucla',     # Eucla (UTC+8:45)
            (-44.0000, -176.5000): 'Pacific/Chatham',    # Chatham Islands (UTC+12:45)
            
            # Date Line & Extreme
            (-13.8333, -171.7667): 'Pacific/Apia',       # Samoa (UTC+13)
            (1.8721, -157.3632): 'Pacific/Kiritimati',   # Kiritimati (UTC+14)
            (51.8800, -176.6581): 'America/Adak',        # Adak (UTC-10)
            
            # Antarctica & Special
            (-77.8460, 166.6680): 'Antarctica/McMurdo',  # McMurdo
            (-64.7742, -64.0531): 'Antarctica/Palmer',   # Palmer
            (78.2232, 15.6267): 'Arctic/Longyearbyen',   # Svalbard
            
            # Complex DST
            (-31.5553, 159.0821): 'Australia/Lord_Howe', # Lord Howe
            (44.9572, 34.1108): 'Europe/Simferopol',     # Crimea
            (33.4484, -112.0740): 'America/Phoenix',     # Arizona (No DST)
        }
        
        def timezone_at_side_effect(lng, lat):
            # Round to 4 decimal places for matching
            lat_rounded = round(lat, 4)
            lng_rounded = round(lng, 4)
            for (coord_lat, coord_lng), tz in timezone_database.items():
                if abs(coord_lat - lat_rounded) < 0.01 and abs(coord_lng - lng_rounded) < 0.01:
                    return tz
            return None
        
        tf_instance.timezone_at.side_effect = timezone_at_side_effect
        yield tf_instance


@pytest.fixture
def mock_streamlit_session_state():
    """Mock Streamlit session state"""
    # Create a wrapper that handles both attribute and item access
    class MockSessionState(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Store internal dict for direct access if needed
            self._state_dict = self
            
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError:
                raise AttributeError(f"st.session_state has no key {key}")
                
        def __setattr__(self, key, value):
            if key == "_state_dict":
                super().__setattr__(key, value)
            else:
                self[key] = value
                
    # Create the mock instance
    mock_state = MockSessionState()
    
    # Patch the importing of session_state in app.py
    with patch('app.st.session_state', mock_state):
        yield mock_state


@pytest.fixture
def mock_streamlit_toast():
    """Mock Streamlit toast notifications"""
    with patch('app.st.toast') as mock_toast:
        yield mock_toast


@pytest.fixture
def clear_cache():
    """Clear Streamlit cache between tests"""
    if hasattr(st, 'cache_data'):
        st.cache_data.clear()
    yield
    if hasattr(st, 'cache_data'):
        st.cache_data.clear()


# ============================================================================
# TEST CLASS: get_timezone_from_string
# ============================================================================

class TestGetTimezoneFromString:
    """Test suite for timezone detection from location queries"""
    
    def test_valid_city_new_york(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test timezone detection for New York City"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("New York")
        
        assert tz == "America/New_York"
        assert "New York" in addr
        assert "USA" in addr
    
    def test_valid_city_london(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test timezone detection for London"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("London")
        
        assert tz == "Europe/London"
        assert "London" in addr
    
    def test_valid_city_tokyo(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test timezone detection for Tokyo"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("Tokyo")
        
        assert tz == "Asia/Tokyo"
        assert "Tokyo" in addr
    
    def test_valid_city_sydney(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test timezone detection for Sydney"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("Sydney")
        
        assert tz == "Australia/Sydney"
        assert "Sydney" in addr
    
    def test_case_insensitivity(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that city names are case insensitive"""
        from app import get_timezone_from_string
        
        # Test various cases
        tz1, _ = get_timezone_from_string("london")
        tz2, _ = get_timezone_from_string("LONDON")
        tz3, _ = get_timezone_from_string("London")
        
        assert tz1 == tz2 == tz3 == "Europe/London"
    
    def test_unicode_characters_sao_paulo(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test handling of Unicode characters (São Paulo)"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("São Paulo")
        
        assert tz == "America/Sao_Paulo"
        assert "São Paulo" in addr
    
    def test_unicode_characters_zurich(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test handling of Unicode characters (Zürich)"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("Zürich")
        
        assert tz == "Europe/Zurich"
        assert "Zürich" in addr
    
    def test_ambiguous_location_paris(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test ambiguous location name (Paris defaults to France)"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("Paris")
        
        assert tz == "Europe/Paris"
        assert "France" in addr
    
    def test_specific_ambiguous_location_paris_texas(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test specific ambiguous location (Paris, Texas)"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("Paris, Texas")
        
        assert tz == "America/Chicago"
        assert "Texas" in addr
    
    def test_whitespace_handling(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that leading/trailing whitespace is handled"""
        from app import get_timezone_from_string
        
        tz1, _ = get_timezone_from_string("  London  ")
        tz2, _ = get_timezone_from_string("London")
        
        assert tz1 == tz2 == "Europe/London"
    
    def test_invalid_location_returns_none(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that invalid location returns (None, None)"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("XyZInvalidCity123")
        
        assert tz is None
        assert addr is None
    
    def test_empty_string_returns_none(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that empty string returns (None, None)"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("")
        
        assert tz is None
        assert addr is None
    
    def test_none_input_returns_none(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that None input returns (None, None)"""
        from app import get_timezone_from_string
        
        # The function should handle None gracefully
        tz, addr = get_timezone_from_string(None)
        
        assert tz is None
        assert addr is None
    
    @patch('app.Nominatim')
    def test_geocoding_timeout_returns_none(self, mock_nom_class, mock_timezonefinder, clear_cache):
        """Test that geocoding timeout returns (None, None)"""
        from app import get_timezone_from_string
        
        # Simulate timeout exception
        geolocator = Mock()
        geolocator.geocode.side_effect = Exception("Timeout")
        mock_nom_class.return_value = geolocator
        
        tz, addr = get_timezone_from_string("London")
        
        assert tz is None
        assert addr is None
    
    @patch('app.Nominatim')
    def test_network_error_returns_none(self, mock_nom_class, mock_timezonefinder, clear_cache):
        """Test that network error returns (None, None)"""
        from app import get_timezone_from_string
        
        # Simulate network error
        geolocator = Mock()
        geolocator.geocode.side_effect = ConnectionError("Network error")
        mock_nom_class.return_value = geolocator
        
        tz, addr = get_timezone_from_string("London")
        
        assert tz is None
        assert addr is None
    
    def test_special_characters_injection_attempt(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test SQL injection attempt is handled safely"""
        from app import get_timezone_from_string
        
        # SQL injection attempt
        tz, addr = get_timezone_from_string("London'; DROP TABLE users; --")
        
        # Should return None (location not found) without crashing
        assert tz is None
        assert addr is None
    
    def test_extremely_long_input(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test extremely long input is handled"""
        from app import get_timezone_from_string
        
        long_input = "A" * 10000
        tz, addr = get_timezone_from_string(long_input)
        
        # Should return None without crashing
        assert tz is None
        assert addr is None
    
    def test_control_characters(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test control characters are handled"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("London\x00\x01\x02")
    # --- NEW COMPLEX TIMEZONE TESTS ---

    def test_offset_30min_india(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test +5:30 offset (India)"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("Delhi")
        assert tz == "Asia/Kolkata"

    def test_offset_45min_nepal(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test +5:45 offset (Nepal)"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("Kathmandu")
        assert tz == "Asia/Kathmandu"

    def test_offset_negative_30min_newfoundland(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test -3:30 offset (Newfoundland)"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("St. John's")
        assert tz == "America/St_Johns"

    def test_weird_offset_eucla(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test +8:45 offset (Eucla, Australia - border town)"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("Eucla")
        assert tz == "Australia/Eucla"

    def test_dateline_samoa(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test UTC+13 (Samoa) - Crossed dateline in 2011"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("Apia")
        assert tz == "Pacific/Apia"

    def test_dateline_kiritimati(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test UTC+14 (Line Islands) - Earliest timezone"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("Kiritimati")
        assert tz == "Pacific/Kiritimati"

    def test_antarctica_stations(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test Antarctica stations (different zones despite same continent)"""
        from app import get_timezone_from_string
        
        tz_mc, _ = get_timezone_from_string("McMurdo Station")
        assert tz_mc == "Antarctica/McMurdo"
        
        tz_pa, _ = get_timezone_from_string("Palmer Station")
        assert tz_pa == "Antarctica/Palmer"

    def test_dst_weirdness_lord_howe(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test Lord Howe Island (0:30 DST delta instead of 1:00)"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("Lord Howe Island")
        assert tz == "Australia/Lord_Howe"

    def test_no_dst_phoenix(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test location with NO DST (Arizona)"""
        from app import get_timezone_from_string
        tz, _ = get_timezone_from_string("Phoenix")
        assert tz == "America/Phoenix"


# ============================================================================
# TEST CLASS: update_timezone_callback
# ============================================================================

class TestUpdateTimezoneCallback:
    """Test suite for Streamlit callback function"""
    
    def test_callback_successful_update(self, mock_geolocator, mock_timezonefinder, 
                                       mock_streamlit_session_state, mock_streamlit_toast, clear_cache):
        """Test callback successfully updates session state on valid location"""
        from app import update_timezone_callback
        
        # Setup: Simulate user entering "London"
        mock_streamlit_session_state._state_dict['loc_input'] = 'London'
        
        # Execute callback
        update_timezone_callback()
        
        # Verify timezone was updated in session state
        assert mock_streamlit_session_state._state_dict['manual_timezone_selector'] == 'Europe/London'
        
        # Verify success toast was shown
        mock_streamlit_toast.assert_called_once()
        call_args = mock_streamlit_toast.call_args
        assert '📍' in call_args[0][0]
        assert 'London' in call_args[0][0]
        assert call_args[1]['icon'] == '✅'
    
    def test_callback_invalid_location(self, mock_geolocator, mock_timezonefinder,
                                      mock_streamlit_session_state, mock_streamlit_toast, clear_cache):
        """Test callback shows error on invalid location"""
        from app import update_timezone_callback
        
        # Setup: Simulate user entering invalid location
        mock_streamlit_session_state._state_dict['loc_input'] = 'InvalidCity123'
        
        # Execute callback
        update_timezone_callback()
        
        # Verify error toast was shown
        mock_streamlit_toast.assert_called_once()
        call_args = mock_streamlit_toast.call_args
        assert '❌' in call_args[0][0]
        assert 'not found' in call_args[0][0]
        assert call_args[1]['icon'] == '⚠️'
    
    def test_callback_empty_input(self, mock_geolocator, mock_timezonefinder,
                                  mock_streamlit_session_state, mock_streamlit_toast, clear_cache):
        """Test callback does nothing on empty input"""
        from app import update_timezone_callback
        
        # Setup: Empty input
        mock_streamlit_session_state._state_dict['loc_input'] = ''
        
        # Execute callback
        update_timezone_callback()
        
        # Verify no toast was shown
        mock_streamlit_toast.assert_not_called()
    
    def test_callback_multiple_cities(self, mock_geolocator, mock_timezonefinder,
                                      mock_streamlit_session_state, mock_streamlit_toast, clear_cache):
        """Test callback works for multiple different cities"""
        from app import update_timezone_callback
        
        test_cities = [
            ('Tokyo', 'Asia/Tokyo'),
            ('Sydney', 'Australia/Sydney'),
            ('Berlin', 'Europe/Berlin'),
        ]
        
        for city, expected_tz in test_cities:
            mock_streamlit_session_state._state_dict['loc_input'] = city
            update_timezone_callback()
            assert mock_streamlit_session_state._state_dict['manual_timezone_selector'] == expected_tz
            mock_streamlit_toast.reset_mock()


# ============================================================================
# TEST CLASS: Caching Behavior
# ============================================================================

class TestCachingBehavior:
    """Test suite for Streamlit caching behavior"""
    
    def test_cache_prevents_redundant_api_calls(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that caching prevents redundant API calls"""
        from app import get_timezone_from_string
        
        # First call - should hit the API
        tz1, addr1 = get_timezone_from_string("London")
        first_call_count = mock_geolocator.geocode.call_count
        
        # Second call with same input - should use cache
        tz2, addr2 = get_timezone_from_string("London")
        second_call_count = mock_geolocator.geocode.call_count
        
        # Results should be identical
        assert tz1 == tz2 == "Europe/London"
        assert addr1 == addr2
        
        # API should only be called once due to caching
        assert second_call_count == first_call_count
    
    def test_different_queries_not_cached_together(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that different queries are cached separately"""
        from app import get_timezone_from_string
        
        # Two different queries
        tz1, _ = get_timezone_from_string("London")
        tz2, _ = get_timezone_from_string("Tokyo")
        
        assert tz1 == "Europe/London"
        assert tz2 == "Asia/Tokyo"
        assert tz1 != tz2


# ============================================================================
# TEST CLASS: Edge Cases & Security
# ============================================================================

class TestEdgeCasesAndSecurity:
    """Test suite for edge cases and security concerns"""
    
    def test_boundary_coordinates(self, mock_timezonefinder, clear_cache):
        """Test coordinates on timezone boundaries"""
        # This tests the TimezoneFinder mock's ability to handle edge coordinates
        tf = mock_timezonefinder
        
        # Test a known coordinate
        tz = tf.timezone_at(lng=-74.0060, lat=40.7128)
        assert tz == "America/New_York"
    
    def test_xss_attempt_in_input(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test XSS attempt in input is handled safely"""
        from app import get_timezone_from_string
        
        xss_input = "<script>alert('XSS')</script>"
        tz, addr = get_timezone_from_string(xss_input)
        
        # Should return None without executing script
        assert tz is None
        assert addr is None
    
    def test_numeric_only_input(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test numeric-only input"""
        from app import get_timezone_from_string
        
        tz, addr = get_timezone_from_string("12345")
        
        # Should return None (not a valid location)
        assert tz is None
        assert addr is None
    
    def test_mixed_language_input(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test mixed language characters"""
        from app import get_timezone_from_string
        
        # Mixed English/Japanese/Cyrillic
        tz, addr = get_timezone_from_string("Tokyo東京москва")
        
        # Should handle gracefully (likely returns None)
        assert isinstance(tz, (str, type(None)))
        assert isinstance(addr, (str, type(None)))


# ============================================================================
# TEST CLASS: Performance
# ============================================================================

class TestPerformance:
    """Test suite for performance benchmarks"""
    
    def test_response_time_with_mocking(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test that mocked API calls are fast"""
        import time
        from app import get_timezone_from_string
        
        start = time.time()
        get_timezone_from_string("London")
        elapsed = time.time() - start
        
        # With mocking, should be very fast (< 100ms)
        assert elapsed < 0.1, f"Response took {elapsed*1000:.2f}ms, expected < 100ms"
    
    def test_batch_processing(self, mock_geolocator, mock_timezonefinder, clear_cache):
        """Test processing multiple locations quickly"""
        import time
        from app import get_timezone_from_string
        
        cities = ["London", "Tokyo", "Sydney", "Berlin", "Moscow"]
        
        start = time.time()
        for city in cities:
            get_timezone_from_string(city)
        elapsed = time.time() - start
        
        # All 5 cities should process in < 500ms with mocking
        assert elapsed < 0.5, f"Batch processing took {elapsed*1000:.2f}ms, expected < 500ms"


# ============================================================================
# PYTEST MARKERS
# ============================================================================

# pytest.mark.slow is defined in pytest.ini


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=html"])
