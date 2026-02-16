# ChronoShift QA Test Suite Documentation

## Overview
Comprehensive `pytest`-based QA automation suite for the ChronoShift timezone conversion application. This suite validates timezone detection logic, handles API mocking to prevent rate limiting, and ensures robust error handling.

## Test Coverage

### 40+ Test Scenarios Across 6 Categories:

#### 1. **Timezone Detection Tests** (18 tests)
- ✅ Valid cities: New York, London, Tokyo, Sydney, Berlin, Moscow
- ✅ Case insensitivity
- ✅ Unicode characters: São Paulo, Zürich
- ✅ Ambiguous locations: Paris (France) vs Paris, Texas
- ✅ Whitespace handling
- ❌ Invalid locations
- ❌ Empty/None inputs
- ❌ Timeout scenarios
- ❌ Network errors

#### 2. **Streamlit Callback Tests** (4 tests)
- Successful session state updates
- Error toasts on invalid locations
- Empty input handling
- Multiple city updates

#### 3. **Caching Behavior Tests** (2 tests)
- Cache prevents redundant API calls
- Different queries cached separately

#### 4. **Edge Cases & Security** (5 tests)
- SQL injection attempts
- XSS attempts
- Extremely long inputs
- Control characters
- Mixed language input

#### 5. **Performance Tests** (2 tests)
- Response time < 100ms (with mocking)
- Batch processing < 500ms for 5 cities

#### 6. **Boundary Tests** (3 tests)
- Timezone boundary coordinates
- Numeric-only inputs
- Special character handling

## Installation

### 1. Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Verify Installation
```bash
pytest --version
```

## Running Tests

### Run All Tests
```bash
pytest qa_suite.py -v
```

### Run with Coverage Report
```bash
pytest qa_suite.py -v --cov=app --cov-report=html
```

### Run Specific Test Categories
```bash
# Run only fast tests (skip slow tests)
pytest qa_suite.py -v -m "not slow"

# Run only security tests
pytest qa_suite.py -v -k "security or injection or xss"

# Run only timezone detection tests
pytest qa_suite.py -v -k "timezone"

# Run only callback tests
pytest qa_suite.py -v -k "callback"
```

### Parallel Execution (Faster)
```bash
pytest qa_suite.py -v -n auto
```

### Generate HTML Coverage Report
```bash
pytest qa_suite.py --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Expected Results

### Test Execution Time
- **Total**: < 5 seconds (all 40+ tests)
- **Individual tests**: < 100ms each

### Coverage Target
- **Line Coverage**: > 85%
- **Branch Coverage**: > 80%

### Sample Output
```
qa_suite.py::TestGetTimezoneFromString::test_valid_city_new_york PASSED
qa_suite.py::TestGetTimezoneFromString::test_valid_city_london PASSED
qa_suite.py::TestGetTimezoneFromString::test_case_insensitivity PASSED
...
========== 40 passed in 3.21s ==========
```

## Mocking Strategy

### Why Mocking?
1. **Prevents API Rate Limiting**: No real calls to Nominatim geocoding service
2. **Fast Execution**: Tests run in milliseconds, not seconds
3. **Reliable**: No dependency on network or external services
4. **Deterministic**: Same inputs always produce same outputs

### What's Mocked?
- ✅ `geopy.geocoders.Nominatim` - Geocoding service
- ✅ `timezonefinder.TimezoneFinder` - Timezone detection
- ✅ `streamlit.session_state` - Session state management
- ✅ `streamlit.toast` - Toast notifications

## Test Data

### Predefined Test Locations
The test suite includes a database of 10 common cities with accurate coordinates and timezones:

| City | Timezone | Coordinates |
|------|----------|-------------|
| New York | America/New_York | 40.7128°N, 74.0060°W |
| London | Europe/London | 51.5074°N, 0.1278°W |
| Tokyo | Asia/Tokyo | 35.6762°N, 139.6503°E |
| Sydney | Australia/Sydney | 33.8688°S, 151.2093°E |
| São Paulo | America/Sao_Paulo | 23.5505°S, 46.6333°W |
| Paris | Europe/Paris | 48.8566°N, 2.3522°E |
| Zürich | Europe/Zurich | 47.3769°N, 8.5417°E |
| Berlin | Europe/Berlin | 52.5200°N, 13.4050°E |
| Moscow | Europe/Moscow | 55.7558°N, 37.6173°E |

## Continuous Integration

### GitHub Actions Example
```yaml
name: QA Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pip install -r requirements-test.txt
      - run: pytest qa_suite.py -v --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Troubleshooting

### Issue: Import Errors
**Solution**: Ensure `app.py` is in the same directory as `qa_suite.py`

### Issue: Streamlit Not Found
**Solution**: Install Streamlit: `pip install streamlit`

### Issue: Cache Not Clearing
**Solution**: The `clear_cache` fixture handles this automatically. If issues persist, manually clear with:
```python
st.cache_data.clear()
```

## Extending the Test Suite

### Adding New Test Locations
Edit the `mock_geolocator` fixture in `qa_suite.py`:

```python
location_database = {
    'your_city': mock_nominatim_location('City, Country', lat, lng),
    # ...
}
```

### Adding New Timezone Mappings
Edit the `mock_timezonefinder` fixture:

```python
timezone_database = {
    (lat, lng): 'Timezone/Name',
    # ...
}
```

## Best Practices

1. **Run tests before commits**: `pytest qa_suite.py -v`
2. **Check coverage regularly**: Target > 85%
3. **Add tests for new features**: Maintain comprehensive coverage
4. **Never skip security tests**: Always validate input sanitization
5. **Keep tests fast**: Each test should complete in < 100ms

## License
Same as ChronoShift application

## Contact
For QA questions or test failures, please open an issue.
