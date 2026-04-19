# Rust DID Implementation Guide for New ByersBrands-Ecosystem Apps
**Purpose:** Standardized setup for new Django apps using Rust DID (FFI + WASM) in the ByersBrands ecosystem.

---

## 1. Architecture Overview
### Hybrid Design (Backend + Frontend)



┌───────────────────────────────────────────────────────────────────────────────┐

│                        ByersBrands-Ecosystem App                              │

├───────────────────────┬───────────────────────┬───────────────────────────────┤

│   Django (Backend)    │   Rust FFI            │   WASM (Frontend)             │

│                       │   (libdid_rust.so)     │   (did_rust.wasm)             │

├───────────────────────┼───────────────────────┼───────────────────────────────┤

│ - User models          │ - DID generation      │ - In-browser DID generation   │

│ - Python fallback      │ - VC verification     │ - Client-side VC verification │

│ - Admin interfaces     │ - VC issuance         │ - Key management              │

└───────────────────────┴───────────────────────┴───────────────────────────────┘


---

## 2. Prerequisites
### Tools
- Rust toolchain (`cargo`, `wasm-pack`)
- Python 3.8+ (Django)
- Node.js (for WASM testing)

### Dependencies
#### Rust (`Cargo.toml`)
```toml
[lib]
crate-type = ["cdylib", "rlib"]  # For FFI + WASM

[dependencies]
ed25519-dalek = { version = "1.0", features = ["wasm"] }
wasm-bindgen = "0.2"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
serde-wasm-bindgen = "0.4"
getrandom = { version = "0.2", features = ["js"] }  # WASM-compatible randomness

[target.'cfg(target_arch = "wasm32")'.dependencies]
# WASM-specific dependencies



Python (requirements.txt)

Django==4.0
didkit==0.3
pydid==0.4




3. Project Setup
A. Skeleton the Django App 


django-admin startproject myapp
cd myapp
mkdir -p apps/accounts/did_rust_wrapper



B. Add Rust DID Repo as Submodule


git submodule add <URL_OF_DID_RUST_REPO> external/did-rust-core
git submodule update --init --recursive



C. Directory Structure

myapp/
├── apps/
│   └── accounts/
│       ├── did_rust_wrapper/   # Rust FFI + WASM wrapper
│       │   ├── __init__.py     # Backend selection logic
│       │   ├── rust_ffi.py     # FFI bindings
│       │   └── wasm_utils.py   # WASM integration helpers
│       ├── utils/
│       │   └── did_utils.py    # Python fallback
│       └── models.py           # User model with DID fields
├── external/
│   └── did-rust-core/          # Submodule: Shared Rust crate
├── static/
│   └── js/                     # WASM output
│       ├── did_rust.js         # WASM bindings
│       └── did_rust.wasm       # WASM binary
└── templates/
    └── did_demo.html           # WASM demo page




4. Rust Implementation
A. Build the Rust Library (FFI + WASM)


# Build for FFI (backend)
cd external/did-rust-core
cargo build --release

# Build for WASM (frontend)
wasm-pack build --target web




Outputs:

target/release/libdid_rust.so (FFI)
pkg/did_rust.js + pkg/did_rust.wasm (WASM)

B. Configure Cargo.toml for Dual Targets
See Prerequisites.
C. Core Traits (Rust)


// external/did-rust-core/src/lib.rs
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct DIDDocument;

#[wasm_bindgen]
impl DIDDocument {
    pub fn generate(method: &str) -> Result<String, JsValue> {
        // Implementation for WASM/FFI
    }

    pub fn verify_vc(vc: &str) -> Result<bool, JsValue> {
        // Implementation
    }

    pub fn issue_vc(credential: &str, did: &str, key: &str) -> Result<String, JsValue> {
        // Implementation
    }
}




5. Django Integration
A. Backend (FFI)
did_rust_wrapper/__init__.py


import os
from django.conf import settings

def get_did_backend():
    if settings.DID_BACKEND == "rust":
        from .rust_ffi import RustDIDFFI
        return RustDIDFFI()
    from ..utils.did_utils import PythonDIDFallback
    return PythonDIDFallback()



did_rust_wrapper/rust_ffi.py


from ctypes import CDLL, c_char_p, c_bool
import os

class RustDIDFFI:
    def __init__(self):
        lib_path = os.path.join(settings.BASE_DIR, "external/did-rust-core/target/release/libdid_rust.so")
        self.lib = CDLL(lib_path)

    def generate_did(self, method: str) -> str:
        self.lib.generate_did_ffi.argtypes = [c_char_p]
        self.lib.generate_did_ffi.restype = c_char_p
        return self.lib.generate_did_ffi(method.encode()).decode()



B. Frontend (WASM)
settings.py


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "external/did-rust-core/pkg"),
]



templates/did_demo.html


{% load static %}
<script type="module">
  import init, { generate_did } from '{% static "js/did_rust.js" %}';

  async function run() {
    await init();
    const did = generate_did("key");
    console.log("Generated DID:", did);
  }
  run();
</script>




6. User Model
apps/accounts/models.py


from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    did = models.CharField(max_length=100, blank=True)
    did_key = models.JSONField(default=dict)  # Stores public/private keys




7. Standardized DID Operations
Backend (Python/Rust FFI)


from apps.accounts.utils.did_utils import generate_did, verify_vc, issue_vc

# Generate a DID
did = generate_did(method="key", key_type="Ed25519")

# Issue a VC
vc = issue_vc(
    credential={"id": did, "claim": {"name": "John Doe"}},
    did=did,
    key=user.did_key
)

# Verify a VC
is_valid = verify_vc(vc)



Frontend (WASM)


// In-browser DID generation
async function generateDid() {
  const did = await window.generate_did("key");
  return did;
}

// Client-side VC verification
async function verifyVc(vc) {
  const isValid = await window.verify_vc(vc);
  return isValid;
}




8. Testing
Rust (FFI + WASM)


# Test FFI
cargo test

# Test WASM
wasm-pack test --node



Django


python manage.py test apps.accounts.tests.test_did



Frontend


<!-- Test WASM in a browser -->
<script type="module">
  import { verify_vc } from '/static/js/did_rust.js';
  // Test VC verification
</script>




9. Deployment
A. Build Script

#!/bin/bash
# Build Rust for FFI and WASM
cd external/did-rust-core
cargo build --release
wasm-pack build --target web

# Collect static files
cp -r pkg/* ../static/js/



B. Environment Variables


# Use Rust backend (FFI)
export DID_BACKEND=rust

# Use Python fallback
export DID_BACKEND=python




10. Roadmap


  
    
      Task
      Timeline
      Owner
    
  
  
    
      Skeleton Django app
      1 day
      Senior Dev
    
    
      Integrate Rust submodule
      1 day
      Coding Agent
    
    
      Implement FFI backend
      1 week
      Coding Agent
    
    
      Add WASM support
      1–2 weeks
      Coding Agent
    
    
      Test WASM in browser
      1 week
      QA/Dev
    
    
      Document WASM API
      1 week
      Senior Dev
    
  



11. Troubleshooting
Common Issues


  
    
      Issue
      Solution
    
  
  
    
      WASM fails to load
      Check STATICFILES_DIRS and file permissions.
    
    
      FFI library not found
      Verify RUST_LIB_PATH in settings.py.
    
    
      Cross-backend verification fails
      Ensure JWS signing is consistent.
    
  


Debugging WASM


# Run a local server for testing
python manage.py runserver

# Open browser console to debug WASM




12. Resources

Rust DID Crate: Repo https://chat.mistral.ai/chat/b3c4f0bd-bf85-4eee-b73c-06d937752802#
W3C DID Core Spec: https://www.w3.org/TR/did-core/
wasm-bindgen Docs: https://rustwasm.github.io/wasm-bindgen/
Django Static Files: https://docs.djangoproject.com/en/4.0/howto/static-files/