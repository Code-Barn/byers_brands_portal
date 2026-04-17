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
├── .venv/                  # Python virtual environment (uv)
├── core/                   # Django project configuration
│   ├── settings/           # Environment-specific settings
│   │   ├── base.py        # Base settings (shared)
│   │   ├── dev.py         # Development settings
│   │   └── prod.py        # Production settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI application
├── apps/                   # Django applications
│   ├── brand/             # Brand showcase app
│   │   ├── models.py      # BrandPage, Product models
│   │   ├── views.py       # Page view handlers
│   │   ├── urls.py        # Brand URL routing
│   │   └── templates/     # Brand page templates
│   └── accounts/           # User authentication app
│       ├── models.py      # CustomUser model with DID support
│       ├── views.py       # Auth views (login, register, DID auth)
│       ├── did_rust_wrapper.py  # Rust FFI wrapper
│       └── templates/     # Auth templates
├── rust_did/              # Rust DID library
│   ├── Cargo.toml         # Rust project manifest
│   ├── src/lib.rs        # FFI implementations
│   └── target/release/   # Compiled library (libdid_rust.so)
├── static/                 # Static files
│   ├── css/               # Custom styles
│   └── js/                # JavaScript utilities
├── templates/              # Global templates
│   └── base.html          # Base template with theme toggle
├── manage.py              # Django management script
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
# Create virtual environment with uv
uv venv

# Activate the environment
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies using uv
uv pip install -r requirements.txt

# Or if using traditional pip
.venv/bin/pip install -r requirements.txt
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
# No setup needed - Django will create db.sqlite3
python manage.py migrate
```

For production (PostgreSQL):
```bash
# Edit core/settings/prod.py with your DB credentials
createdb byers_brands
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
# Use development settings
DJANGO_SETTINGS_MODULE=core.settings.dev python manage.py runserver

# Or simply
python manage.py runserver
```

Visit http://localhost:8000 to view the site.

---

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SETTINGS_MODULE` | Django settings module | `core.settings.dev` | Yes |
| `DJANGO_SECRET_KEY` | Django secret key | Generated | No |
| `DID_BACKEND` | DID implementation | `rust` | No |
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
DID_BACKEND=rust
```

---

## Configuration Options

### DID Backend Toggle

The portal supports both Rust and Python DID implementations:

```bash
# Use Rust FFI library (default, recommended)
DID_BACKEND=rust python manage.py runserver

# Use Python fallback implementation
DID_BACKEND=python python manage.py runserver
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
| `/accounts/dashboard/` | Investor dashboard (coming soon) |
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

### DID Implementation
- **Language**: Rust 1.70+
- **Interface**: FFI (Foreign Function Interface)
- **Library**: `libdid_rust.so` (compiled)
- **Functions**: DID generation, VC verification, VC issuance

### Infrastructure
- **Package Manager**: uv
- **Static Files**: Django Compressor (optional)
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

## Customization

### Brand Colors

The brand color (#0064aa) is defined in multiple places:

1. **CSS Variables** (`static/css/styles.css`):
   ```css
   :root {
       --brand-blue: #0064aa;
   }
   ```

2. **Django Settings** (`core/settings/base.py`):
   ```python
   BRAND_COLOR = '#0064aa'
   ```

3. **Tailwind Config** (via CDN): Custom colors can be added

### Branding Assets

To add your logos and assets:

1. Place logo files in `static/images/`
2. Update `templates/base.html` to reference your logo
3. Update the brand name in navigation

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
RUN python manage.py collectstatic --noinput

# Run
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
```

### Manual Deployment

```bash
# Collect static files
python manage.py collectstatic

# Run with Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 core.wsgi:application

# Run with uWSGI
pip install uwsgi
uwsgi --http :8000 --module core.wsgi --workers 4
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
python manage.py test
```

### Code Quality

```bash
# Formatting
black .

# Linting
flake8 .

# Import sorting
isort .
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Manage.py Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Shell
python manage.py shell

# Collect static
python manage.py collectstatic

# Show URLs
python manage.py show_urls
```

---

## Future Direction (Phase 2)

The following features are planned for Phase 2:

### Polly Integration
- Multi-signature wallet support
- Transaction signing via DID
- Governance voting

### Investor Tools
- Portfolio tracking
- Real-time analytics dashboard
- Document management
- Investment opportunities
- ROI calculator

### Enhanced Authentication
- WebAuthn support
- Magic links
- Social login (optional)

### Additional Features
- Admin dashboard
- CRM integration
- Email notifications
- API v2 (GraphQL)

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

2. Check the library path in `core/settings/base.py`:
   ```python
   RUST_DID_LIB_PATH = os.path.join(BASE_DIR, 'rust_did', 'target', 'release', 'libdid_rust.so')
   ```

3. Fall back to Python implementation:
   ```bash
   DID_BACKEND=python python manage.py runserver
   ```

### Database Issues

For SQLite errors:
```bash
rm db.sqlite3
python manage.py migrate
```

For PostgreSQL connection issues:
1. Verify credentials in `core/settings/prod.py`
2. Ensure PostgreSQL is running
3. Check firewall settings

### Static Files Not Loading

```bash
python manage.py collectstatic
# Ensure STATIC_ROOT is writable
```

---

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Changelog

### Phase 1 (Current)
- Initial Django project setup
- Brand showcase pages (Home, About, Products, Contact)
- Rust/DID authentication integration
- Light/Dark mode with brand color #0064aa
- Responsible mobile design
- Investor dashboard placeholder
- Custom user model with DID support
- Static page templates with Tailwind CSS

### Next
- Phase 2: Polly integration and investor tools
- Phase 3: Advanced features and optimizations
