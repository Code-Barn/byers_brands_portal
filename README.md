# Byers Brands Web Portal

A Django-based web portal for Byers Brands, featuring brand showcase pages, Rust/DID authentication, and investor engagement tools.

## Preview

The Phase 1 implementation includes:
- **Brand Showcase**: Home, About Us, Products, Contact pages
- **DID Authentication**: Decentralized identity login via Rust FFI library
- **Light/Dark Mode**: Theme toggle with brand color #0064aa
- **Investor Dashboard**: Placeholder for Phase 2 features

## Project Structure

```
byers_brands_portal/
├── config/                  # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py            # Main URL configuration
│   └── settings/
│       ├── base.py        # Base settings (shared)
│       ├── dev.py         # Development settings
│       └── prod.py        # Production settings
├── apps/                   # Django applications
│   ├── core/              # Shared resources and base templates
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── templates/
│   │   │   └── base.html          # Base template with theme toggle
│   │   └── static/
│   │       ├── css/
│   │       │   └── styles.css     # Custom styles with brand color
│   │       ├── js/
│   │       │   ├── theme.js       # Theme toggle functionality
│   │       │   └── mobile-menu.js # Mobile navigation
│   │       └── images/
│   │           ├── LOGO.png       # Light mode logo
│   │           ├── DM_LOGO.PNG    # Dark mode logo
│   │           ├── LOGO_FULL.png  # Light mode full logo
│   │           └── DM_LOGO_FULL.PNG # Dark mode full logo
│   ├── brand/             # Brand showcase app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py      # BrandPage, Product models
│   │   ├── urls.py        # Brand URL routing
│   │   ├── views.py       # Page view handlers
│   │   └── templates/
│   │       └── brand/
│   │           ├── home.html
│   │           ├── about.html
│   │           ├── products.html
│   │           ├── contact.html
│   │           └── product_detail.html
│   └── accounts/           # User authentication app
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py      # CustomUser model with DID support
│       ├── did_rust_wrapper.py  # Rust FFI integration
│       ├── urls.py
│       ├── views.py       # Auth views (login, register, DID auth)
│       └── templates/
│           └── accounts/
│               ├── login.html
│               ├── register.html
│               ├── did_login.html
│               ├── profile.html
│               └── investor_dashboard.html
├── rust_did/              # Rust DID library
│   ├── Cargo.toml         # Rust project manifest
│   ├── src/
│   │   └── lib.rs        # FFI implementations
│   └── target/release/
│       └── libdid_rust.so # Compiled library
├── manage.py              # Django management script
├── pyproject.toml         # Project metadata for uv
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+ (Tested with 3.13.5)
- Rust 1.70+ (for building DID library)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- PostgreSQL (for production)

### 1. Clone the Repository

```bash
cd byers_brands_portal
```

### 2. Set Up Python Environment

```bash
# Create virtual environment with uv (optional - uv will auto-create one)
uv venv

# Activate the environment (optional with uv run)
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies using uv
uv pip install -r requirements.txt

# Or for development with dev tools (black, flake8, isort)
uv pip install -r requirements.txt black flake8 isort
```

### 4. Build Rust DID Library

The Rust library should already be built. If not:

```bash
cd rust_did
cargo build --release
cd ..
```

This generates `rust_did/target/release/libdid_rust.so`

### 5. Set Up Database

For development (SQLite):
```bash
# Django will create db.sqlite3 automatically
uv run python manage.py migrate
```

For production (PostgreSQL):
```bash
# Edit config/settings/prod.py with your DB credentials
createdb byers_brands
DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
uv run python manage.py createsuperuser
```

### 7. Run Development Server

```bash
# Use development settings (default in manage.py)
uv run python manage.py runserver
```

Visit **http://localhost:8000** to view the site.

---

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SETTINGS_MODULE` | Django settings module | `config.settings.dev` | Yes |
| `DJANGO_SECRET_KEY` | Django secret key | Generated | No |
| `DID_BACKEND` | DID implementation | `python` | No |
| `DB_NAME` | Database name | `byers_brands` | No |
| `DB_USER` | Database user | `postgres` | No |
| `DB_PASSWORD` | Database password | `postgres` | No |
| `DB_HOST` | Database host | `localhost` | No |
| `DB_PORT` | Database port | `5432` | No |
| `DEBUG` | Debug mode | `True` | No |

### For Development

Create a `.env` file:

```bash
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DID_BACKEND=python
```

---

## Configuration Options

### DID Backend Toggle

The portal supports both Rust and Python DID implementations:

```bash
# Use Rust FFI library
DID_BACKEND=rust uv run python manage.py runserver

# Use Python fallback (recommended for now)
DID_BACKEND=python uv run python manage.py runserver
```

### Theme Mode

- Light mode (default)
- Dark mode (toggle via button in top-right corner)
- System preference (automatic)
- Persists in localStorage

---

## URL Routing

### Public Pages
| URL | Description |
|-----|-------------|
| `/` | Home page (Brand showcase) |
| `/about/` | About Us page |
| `/products/` | Products listing |
| `/products/<id>/` | Product detail |
| `/contact/` | Contact page |

### Authentication
| URL | Description |
|-----|-------------|
| `/accounts/login/` | Email/Password login |
| `/accounts/register/` | User registration |
| `/accounts/did-login/` | DID-based authentication |
| `/accounts/logout/` | Logout |
| `/accounts/profile/` | User profile |
| `/accounts/dashboard/` | Investor dashboard (placeholder) |
| `/investor/` | Investor dashboard alias |

### API Endpoints
| URL | Method | Description |
|-----|--------|-------------|
| `/accounts/api/generate-did/` | GET | Generate a new DID |
| `/accounts/api/verify-vc/` | POST | Verify Verifiable Credential |
| `/accounts/api/challenge/` | GET | Generate authentication challenge |

---

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **Language**: Python 3.10+
- **Database**: PostgreSQL (SQLite for development)
- **Authentication**: DID (Decentralized Identifier)
- **REST**: Django REST Framework

### Frontend
- **CSS**: Tailwind CSS (CDN)
- **JavaScript**: Vanilla JS
- **Components**: Custom HTML templates
- **Dark Mode**: Tailwind CSS class-based

### DID Implementation
- **Language**: Rust 1.70+
- **Interface**: FFI (Foreign Function Interface)
- **Library**: `libdid_rust.so` (compiled)
- **Functions**: DID generation, VC verification, VC issuance

### Infrastructure
- **Package Manager**: uv
- **Static Files**: Django staticfiles framework
- **Security**: HTTPS, CSRF protection, HSTS

---

## Rust/DID Integration

### Library Functions (FFI)

The Rust library provides these functions via FFI:

| Function | Arguments | Returns | Description |
|----------|-----------|---------|-------------|
| `generate_did_ffi` | `method: *const c_char` | `*mut c_char` | Generate DID |
| `verify_vc_ffi` | `vc: *const c_char` | `bool` | Verify VC |
| `issue_vc_ffi` | `credential, did, key: *const c_char` | `*mut c_char` | Issue VC |
| `free_string` | `ptr: *mut c_char` | `()` | Free C string |

### Python Wrapper

The `did_rust_wrapper.py` module provides a clean Python interface:

```python
from apps.accounts.did_rust_wrapper import (
    generate_did,
    verify_vc,
    issue_vc,
    get_did_backend
)

# Generate a DID
did = generate_did('key')

# Verify a Verifiable Credential
valid = verify_vc(vc_json)

# Get the backend (Rust or Python fallback)
backend = get_did_backend()
did = backend.generate_did('key')
```

### Fallback Implementation

If the Rust library is unavailable, a Python fallback is used automatically.

---

## Dark Mode Implementation

### How It Works

1. **HTML Class**: The `<html>` element gets a `dark` class when dark mode is active
2. **Tailwind Classes**: All elements use `dark:` prefixed classes (e.g., `dark:bg-gray-900`)
3. **Toggle Button**: Clicking the button in the top-right toggles the `dark` class
4. **Local Storage**: Preference is saved and restored on page load
5. **Logo Switching**: Light/dark mode logos switch automatically via CSS classes

### Customization

Base colors in `apps/core/static/css/styles.css`:
```css
:root {
    --brand-blue: #0064aa;
}
```

---

## Deployment

### Docker (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Build Rust library
RUN cd rust_did && cargo build --release

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Run
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### Manual Deployment

```bash
# Collect static files
uv run python manage.py collectstatic

# Run with Gunicorn
uv pip install gunicorn
uv run gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application

# Run with uWSGI
uv pip install uwsgi
uv run uwsgi --http :8000 --module config.wsgi --workers 4
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location /static/ {
        alias /path/to/byers_brands_portal/staticfiles/;
    }

    location /media/ {
        alias /path/to/byers_brands_portal/media/;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Development Notes

### Running Tests

```bash
uv run python manage.py test
```

### Code Quality

```bash
# Formatting
uv run black .

# Linting
uv run flake8 .

# Import sorting
uv run isort .
```

### Creating Migrations

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Manage.py Commands

```bash
# Create superuser
uv run python manage.py createsuperuser

# Run server
uv run python manage.py runserver

# Shell
uv run python manage.py shell

# Collect static
uv run python manage.py collectstatic

# Show URLs
uv run python manage.py show_urls
```

---

## Future Direction (Phase 2)

The following features are now implemented in Phase 2, Week 1:

### Completed - Investor Tools
- Portfolio tracking with Django models and REST API
- Real-time analytics dashboard with Chart.js
- Document management (upload/download, 10MB limit, PDF/DOC/images)
- Investment opportunities listing
- ROI calculator with real-time calculation

### Completed - Polly Integration
- Remote API client for Polly polls (`apps/polly_client/`)
- Embeddable poll widgets with scope-aware filtering
- Cactus Comments integration for discussion threads
- Theme-aware rendering (light/dark mode)

### In Progress - Authentication
- Full DID-Rust authentication flow
- Session-based DID persistence
- API endpoints for VC verification

### Next
- Phase 2, Week 2+ features (as needed)
- WebAuthn support
- Enhanced security
- Admin dashboard

---

## Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **CSRF Protection**: Django's CSRF middleware is enabled
3. **HSTS**: HTTP Strict Transport Security is enabled
4. **Secure Cookies**: Session and CSRF cookies are Secure
5. **CORS**: Configure properly for API access
6. **DID Verification**: Always verify DID signatures server-side

---

## Troubleshooting

### Rust Library Loading Issues

If you see `Could not load Rust DID library`:

1. Ensure the library is built:
   ```bash
   cd rust_did
   cargo build --release
   cd ..
   ```

2. Check the library path in `config/settings/base.py`:
   ```python
   RUST_DID_LIB_PATH = os.path.join(BASE_DIR.parent, 'rust_did', 'target', 'release', 'libdid_rust.so')
   ```

3. Fall back to Python implementation:
   ```bash
   DID_BACKEND=python uv run python manage.py runserver
   ```

### Database Issues

For SQLite errors:
```bash
rm db.sqlite3
uv run python manage.py migrate
```

For PostgreSQL connection issues:
1. Verify credentials in `config/settings/prod.py`
2. Ensure PostgreSQL is running
3. Check firewall settings

### Static Files Not Loading

```bash
uv run python manage.py collectstatic
# Ensure STATIC_ROOT is writable
```

### Theme Toggle Not Working

1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Check browser console for JavaScript errors
3. Verify `/static/js/theme.js` loads in browser dev tools
4. Ensure you're using `uv run python manage.py runserver` or have `DJANGO_SETTINGS_MODULE=config.settings.dev` set

---

## License

MIT License

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Changelog

### Phase 2, Week 1 (Current)
- **Investor Dashboard Expansion**:
  - Portfolio tracking with Investment model and REST API
  - Real-time analytics with Chart.js integration
  - Document management with file upload/download
  - Investment opportunities listing
  - Interactive ROI calculator
- **Polly Integration**:
  - `apps/polly_client/` for remote Polly API integration
  - Scope-aware poll widgets with `byers-brands-llc` embedding app
  - Cactus Comments integration for poll discussions
- **Playwright Test Suite**:
  - `tests/playwright/` with conftest, test_dashboard.py, test_polly.py, test_auth.py
- **DID-Rust Authentication**:
  - Full integration with existing DID backend
  - Session persistence of DID for Polly API calls

### Phase 1 (Current)
- Initial Django project setup with config/ structure
- Brand showcase pages (Home, About, Products, Contact)
- Rust/DID authentication integration
- Light/Dark mode with brand color #0064aa
- Responsive mobile design
- Investor dashboard placeholder
- Custom user model with DID support
- Static page templates with Tailwind CSS
- Shared resources in apps/core/ (templates, static files)

### Next
- Phase 2: Polly integration and investor tools
- Phase 3: Advanced features and optimizations
