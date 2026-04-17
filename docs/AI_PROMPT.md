# AI Development Prompt for Byers Brands Web Portal

## Overview
You are an expert Django developer building **Phase 1** of the **Byers Brands Web Portal**. 
This is a premium Django-based web application featuring:
- Brand showcase pages (Home, About, Products, Contact)
- Rust/DID authentication system
- Light/Dark mode with brand color #0064aa
- Investor dashboard placeholder for Phase 2

## Project Structure

```
byers_brands_portal/
├── config/                  # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   └── settings/
│       ├── base.py        # Base settings (shared)
│       ├── dev.py         # Development settings
│       └── prod.py        # Production settings
├── apps/
│   ├── core/              # Shared resources
│   │   ├── templates/
│   │   │   └── base.html   # Base template with theme toggle
│   │   └── static/
│   │       ├── css/styles.css
│   │       ├── js/theme.js, mobile-menu.js
│   │       └── images/ (logos)
│   ├── brand/             # Brand showcase app
│   │   ├── models.py      # BrandPage, Product
│   │   ├── views.py       # Page view handlers
│   │   ├── urls.py
│   │   └── templates/brand/ (home, about, products, contact)
│   └── accounts/          # User authentication & DID
│       ├── models.py     # CustomUser with DID support
│       ├── views.py      # Auth views
│       ├── did_rust_wrapper.py  # Rust FFI integration
│       ├── forms.py
│       ├── urls.py
│       └── templates/accounts/ (login, register, etc.)
├── rust_did/              # Rust DID library
│   ├── Cargo.toml
│   └── src/lib.rs        # FFI functions
├── manage.py
├── requirements.txt
└── README.md
```

## Development Rules

### 1. Coding Standards
- Use Django 4.x LTS
- Use Tailwind CSS via CDN for styling
- Follow Django best practices
- All views require `@csrf_protect` decorator for forms
- Use `{% load static %}` for all static assets

### 2. Naming Conventions
- Apps: lowercase, singular (e.g., `accounts`, `brand`, `core`)
- Models: PascalCase (e.g., `CustomUser`, `BrandPage`)
- Views: snake_case (e.g., `user_login`, `generate_did`)
- URLs: hyphenated (e.g., `did-login`, `investor-dashboard`)
- Templates: lowercase with underscores (e.g., `did_login.html`)

### 3. Security Requirements
- Always use HTTPS in production
- Enable CSRF protection on all POST forms
- Use Django's built-in security middleware
- Never hardcode secrets
- Use environment variables for sensitive data
- Validate and sanitize all user input
- Use parameterized queries to prevent SQL injection

### 4. Brand Guidelines
- **Primary Color**: #0064aa (Blue)
- Font: System sans-serif stack (Tailwind default)
- Logo placement: Top-left (navigation), Footer
- Consistent spacing: Use Tailwind spacing scale (4, 6, 8, 12, etc.)

### 5. Template Structure
- Always extend `base.html`
- Use `{% block content %}` for main content
- Include `{% load static %}` at the top
- Use proper HTML5 semantics
- Accessible color contrast (AA minimum)

### 6. Rust/DID Integration
- Use FFI for Rust library (`libdid_rust.so`)
- Python fallback for development/testing
- Wrap all Rust calls in try/except blocks
- DID format: `did:key:{unique_id}`
- Store DID in CustomUser.did field

## Common Tasks

### Adding a New Page
1. Create template in `apps/{app}/templates/{app}/`
2. Add view function in `apps/{app}/views.py`
3. Add URL pattern in `apps/{app}/urls.py`
4. Extend `base.html`
5. Add to navigation in `base.html`

### Adding Static Asset
1. Place in `apps/core/static/` (CSS, JS, images)
2. Reference with `{% static 'path/to/file.ext' %}`
3. Use Tailwind classes for styling

### Adding API Endpoint
1. Create view in appropriate app
2. Return JsonResponse
3. Add URL in app's urls.py
4. Use `@csrf_exempt` if needed (API-only)

## Testing
- Run `python manage.py check` before commit
- Test in both light and dark mode
- Verify mobile responsiveness
- Test all links and buttons
- Check form submissions

## Phase 2 Preparation
- Investor dashboard will be expanded
- Polly integration (Polly is separate project)
- Multi-signature wallet support
- Enhanced authentication (WebAuthn, Magic Links)
- Portfolio tracking features

## Important Notes
- Never commit secrets to repository
- Use `.gitignore` for local files
- Keep dependencies updated
- Document all major changes
- Follow semantic versioning
