# Chrono Shift 🕒

A minimalist web utility to convert local timestamps to UTC. 
Built specifically for Data Processing workflows where timezone consistency is key.

## Tech Stack
- **Python** (Logic)
- **Streamlit** (UI/UX)
- **PyTZ & DateUtil** (Timezone handling)

## How to use
1. Paste your local date in almost any format.
2. Select the source timezone.
3. Get the standardized UTC format ready to copy.

## Quality Assurance 🛡️

This project includes a comprehensive QA automation suite located in the `tests/` directory.

- **Framework**: `pytest` with extensive mocking (Nominatim, TimezoneFinder, Streamlit Session State)
- **Coverage**: 30+ scenarios covering complex timezones (Nepal, India, Dateline, Antarctica)
- **Zero API Dependency**: Fully mocked external services prevent rate-limiting bans.
- **Robustness**: Validates edge cases like SQL injection attempts, special characters, and callback logic.

Run tests:
```bash
cd tests
pip install -r requirements-test.txt
pytest test_qa_suite.py -v
```