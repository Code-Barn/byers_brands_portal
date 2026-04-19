Standardized Rust DID Implementation Guidelines for New ByersBrands-Ecosystem Apps
Goal: Build a new Django app within the ByersBrands ecosystem using the standardized Rust DID architecture, ensuring full compatibility with Polly, Byers Brands, and Namechart.

1. Architecture Overview

Hybrid Python/Rust Design:

Use Django for the web layer.
Implement DID operations (generate, verify, issue) via a Rust FFI library (libdid_rust.so).
Fall back to Python/didkit for stability during development.

Backend Selection:

Control backend choice with the DID_BACKEND environment variable:
bash
Copy

DID_BACKEND=rust   # Use Rust (recommended for production)
DID_BACKEND=python # Use Python/didkit (fallback)






2. Core Components to Implement
A. Django Structure

Directory Layout:
bash
Copy

apps/
├── accounts/
│   ├── did_rust_wrapper/   # Rust FFI wrapper and backend selection
│   │   ├── __init__.py     # Backend logic
│   │   ├── rust_ffi.py     # FFI bindings
│   │   └── test_wrapper.py # Tests
│   ├── utils/
│   │   └── did_utils.py    # Main DID utilities (Python fallback)
│   └── models.py           # User model with DID/key storage




B. Rust FFI Requirements

Traits to Implement (Rust):
rust
Copy

// In your shared `did-rust-core` crate (or fork of Byers Brands’ repo)
pub trait DIDDocument {
    fn generate(method: &str) -> Result<String, DIDError>;
    fn verify_vc(vc: &str) -> Result<bool, DIDError>;
    fn issue_vc(credential: &str, did: &str, key: &str) -> Result<String, DIDError>;
}




FFI Signatures:

Export these functions in lib.rs:
rust
Copy

#[no_mangle]
pub extern "C" fn generate_did_ffi(method: *const c_char) -> *mut c_char;
#[no_mangle]
pub extern "C" fn verify_vc_ffi(vc: *const c_char) -> bool;
#[no_mangle]
pub extern "C" fn issue_vc_ffi(credential: *const c_char, did: *const c_char, key: *const c_char) -> *mut c_char;




C. Python Wrapper

Backend Selection Logic:
python
Copy

# In did_rust_wrapper/__init__.py
def get_did_backend():
    if settings.DID_BACKEND == "rust":
        return RustDIDFFI()  # Use Rust FFI
    return PythonDIDFallback()  # Fallback to didkit




FFI Bindings:

Use ctypes or PyO3 to call Rust functions (see Byers Brands’ rust_ffi.py for reference).
D. User Model

DID/Key Storage:

Add these fields to your Django User model:
python
Copy

class User(AbstractUser):
    did = models.CharField(max_length=100, blank=True)
    did_key = models.JSONField(default=dict)  # Stores public/private keys





3. Dependencies

Rust Crate:
toml
Copy

# Cargo.toml
[dependencies]
ed25519-dalek = "1.0"  # For cryptographic operations
serde_json = "1.0"      # For DID document serialization
thiserror = "1.0"       # For error handling




Python:
toml
Copy

# requirements.txt
didkit == 0.3
pydid == 0.4





4. Standardized Workflows
A. DID Operations

Generate a DID:
python
Copy

from apps.accounts.utils.did_utils import generate_did
did = generate_did(method="key", key_type="Ed25519")




Issue a Verifiable Credential:
python
Copy

vc = issue_vc(
    credential={"id": did, "claim": {"name": "John Doe"}},
    did=did,
    key=user.did_key
)




Verify a VC:
python
Copy

is_valid = verify_vc(vc)




B. Testing

Test Coverage Requirements:

Write tests for:

DID generation/validation.
VC issuance/verification (cross-backend).
Error handling (e.g., invalid DIDs/VCs).

Use Byers Brands’ shared test suite as a template.


5. Integration Steps

Set Up Rust Crate:

Fork or reference the shared did-rust-core crate from Byers Brands.
Build the Rust library:
bash
Copy

cd /path/to/did_rust
cargo build --release





Configure Django:

Add DID_BACKEND=rust to your .env file.
Update settings.py to include the Rust library path:
python
Copy

RUST_LIB_PATH = "/path/to/did_rust/target/release/libdid_rust.so"





Implement FFI Wrapper:

Copy did_rust_wrapper/ from Byers Brands and adapt for your app.

Run Tests:

Verify Rust/Python interoperability:
bash
Copy

python manage.py test apps.accounts.tests.test_did






6. Coding Agent Prompt Template

"Build a new Django app in the ByersBrands ecosystem with standardized Rust DID support. Follow these guidelines:

Use the hybrid Python/Rust architecture described above.
Implement the Rust traits and FFI signatures exactly as outlined.
Adopt the directory structure for did_rust_wrapper and did_utils.py.
Use the shared did-rust-core crate for Rust logic.
Ensure all DID operations (generate, verify, issue) work with both Rust and Python backends.
Write tests for cross-backend compatibility.

Start by forking the Byers Brands did_rust repo and setting up the Django project structure. Report back with the skeleton code for review."


7. Resources

Reference Repos:

Byers Brands: [Repo Link]
Shared Rust Crate: [Repo Link]

Documentation:

W3C DID Core Spec
didkit Python docs
ed25519-dalek Rust docs

