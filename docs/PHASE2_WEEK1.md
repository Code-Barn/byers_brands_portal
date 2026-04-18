# Phase 2, Week 1 - Implementation Notes

## Overview
This document captures implementation details for Phase 2, Week 1 of the Byers Brands Web Portal.

## DID-Rust Implementation Status

### Current State
- The Byers Brands Portal uses the DID-Rust implementation as the reference implementation
- Rust library is built at `rust_did/target/release/libdid_rust.so`
- Python fallback available when Rust library is unavailable
- Settings controlled via `DID_BACKEND` environment variable

### Implementation Details
- **Backend Selection**: `DID_BACKEND=python` (default) or `DID_BACKEND=rust`
- **FFI Library**: Loaded via ctypes from configured path
- **User Model**: CustomUser extended with `did` and `did_document` fields

### Future Standardization
The approach used here in Byers Brands Portal will be standardized across:
1. **Namechart** - Future integration
2. **Polly** - Already has similar DID implementation
3. **Other Byers Brands apps** - As needed

## Polly Integration

### Architecture
- **Remote API Approach**: Byers Brands Portal fetches polls from Polly server via HTTP
- **API Base URL**: Configured via `POLLY_API_URL` (default: http://localhost:8001)
- **Embedding App**: `byers-brands-llc`

### API Endpoints Used
- `GET /api/embed/polls/` - Fetch poll list
- `GET /api/embed/polls/{id}/` - Fetch single poll
- `POST /api/polls/{id}/vote/` - Submit vote

### Scope-Aware Filtering
- Polls filtered by user's DID and associated credentials
- Public polls visible to all
- Family-scoped polls require matching credential scope

### Cactus Comments
- Site name: `byers-brands-llc`
- Default homeserver: `https://matrix.cactus.chat:8448`
- Server name: `cactus.chat`

## Investor Dashboard Features

### Portfolio Tracking
- **Models**: Investment, Portfolio (OneToOne with User)
- **API**: `/investor/api/investments/`, `/investor/api/portfolio/summary/`
- **Features**: Add/track investments, view returns, portfolio value

### Document Management
- **Model**: Document with file upload
- **Max File Size**: 10MB
- **Allowed Types**: PDF, images (JPEG, PNG, GIF), Word docs

### Investment Opportunities
- **Model**: InvestmentOpportunity
- **Features**: Display available opportunities, min/max investment, expected returns

### ROI Calculator
- **JavaScript**: Real-time calculation in dashboard
- **Inputs**: Initial investment, monthly contribution, expected return %, years
- **Outputs**: Future value, total contributed, total interest, return %

## Testing

### Playwright Tests
- Location: `/tests/playwright/`
- Run with: `playwright test`
- Coverage: Dashboard UI, theme toggle, Polly integration, auth flows

### To Run Tests
```bash
# Install Playwright browsers
playwright install

# Run tests
cd /home/user/CODE_BASE/byers_brands_portal
export DJANGO_SETTINGS_MODULE=config.settings.dev
playwright test
```

## Configuration

### Environment Variables
```
DJANGO_SETTINGS_MODULE=config.settings.dev
POLLY_API_URL=http://localhost:8001
DID_BACKEND=python
CORS_ALLOW_ALL_ORIGINS=True
```

### Key Settings (in config/settings/base.py)
- `POLLY_API_URL` - Polly server URL
- `POLLY_EMBEDDING_APP` - App identifier for Polly
- `CACTUS_SITE_NAME` - Cactus Comments site identifier
- `CACTUS_HOMESERVER_URL` - Matrix homeserver for comments

## Files Created

### New Apps
- `apps/investor/` - Portfolio, documents, opportunities, ROI calculator
- `apps/polly_client/` - Polly API client, poll widgets, Cactus Comments

### New Tests
- `tests/playwright/conftest.py` - Pytest fixtures
- `tests/playwright/test_dashboard.py` - Dashboard UI tests
- `tests/playwright/test_polly.py` - Polly integration tests
- `tests/playwright/test_auth.py` - DID authentication tests

### New Configuration
- `pytest.ini` - Test configuration
- Updated `requirements.txt` with new dependencies

## Notes for Future Development

1. **Polly Backend**: When Polly is running, polls will appear in the dashboard
2. **Cactus Comments**: Matrix server setup in progress; will work with cactus.chat default
3. **Database**: Currently using SQLite for dev; switch to PostgreSQL for production
4. **DID Standardization**: Coordinate with Polly and Namechart agents for cross-app DID compatibility