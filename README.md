# Byers Brands Web Portal

A Django-based web portal for Byers Brands, featuring brand showcase, Rust/DID authentication, and investor engagement tools.

## Project Structure
byers_brands_portal/

├── core/                  # Core Django settings and utilities

├── apps/                  # Django apps (brand, accounts)

├── rust_did/              # Rust/DID authentication module

├── static/                # Global static files

├── templates/             # Global templates

└── manage.py              # Django management script

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/dcbyers13/byers_brands_portal.git
   cd byers_brands_portal

2. Install dependencies:
   pip install -r requirements.txt

3. Run the development server:
   python manage.py runserver
