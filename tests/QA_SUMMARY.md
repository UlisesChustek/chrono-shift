# QA Test Suite Update

## 1. The "Bug" Explained
The bug was in the **test harness**, not your application code.
- **Issue**: The initial `st.session_state` mock only supported dictionary-style access (`state['key']`).
- **Conflict**: Your app uses attribute-style access (`state.key`).
- **Fix**: Updated the mock to support both access patterns, mirroring Streamlit's actual behavior.

## 2. Expanded Test Coverage
Added **9 new scenarios** (totaling 39 tests) covering complex "weird" timezones:

### New Cases Verified:
- **Non-Integer Offsets**:
  - 🇮🇳 India (`Asia/Kolkata` +5:30)
  - 🇳🇵 Nepal (`Asia/Kathmandu` +5:45)
  - 🇨🇦 Newfoundland (`America/St_Johns` -3:30)
  - 🇦🇺 Eucla (`Australia/Eucla` +8:45)
  
- **Date Line Extremes**:
  - 🇼🇸 Samoa (`Pacific/Apia` +13:00)
  - 🇰🇮 Kiritimati (`Pacific/Kiritimati` +14:00)

- **Antarctica**:
  - McMurdo Station (uses NZ time)
  - Palmer Station (uses Chile time)

- **DST Anomalies**:
  - Lord Howe Island (30-min DST shift)
  - Arizona (No DST)

### Status
✅ **39/39 Tests Passed**
