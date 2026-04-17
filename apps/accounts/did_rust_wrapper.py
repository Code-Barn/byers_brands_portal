"""
Python wrapper for Rust DID FFI library.
Provides a clean interface for DID operations using the compiled Rust library.
"""
import ctypes
import os
import json
from django.conf import settings
from pathlib import Path


class DIDRustWrapper:
    """
    Wrapper class for Rust DID FFI operations.
    Loads the compiled Rust library and provides Python-friendly methods.
    """
    _instance = None
    _lib = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._lib is None:
            self._load_library()
    
    def _load_library(self):
        """Load the Rust FFI library."""
        lib_path = getattr(settings, 'RUST_DID_LIB_PATH', None)
        
        # Try multiple possible paths
        possible_paths = [
            lib_path,
            str(Path(__file__).parent.parent.parent.parent / 'rust_did' / 'target' / 'release' / 'libdid_rust.so'),
            '/home/user/CODE_BASE/byers_brands_portal/rust_did/target/release/libdid_rust.so',
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                try:
                    self._lib = ctypes.CDLL(path)
                    break
                except Exception as e:
                    print(f"Failed to load library from {path}: {e}")
                    continue
        
        if self._lib is None:
            raise RuntimeError(
                "Could not load Rust DID library. "
                "Please build it first: cd rust_did && cargo build --release"
            )
        
        # Define function signatures
        self._lib.generate_did_ffi.argtypes = [ctypes.c_char_p]
        self._lib.generate_did_ffi.restype = ctypes.c_char_p
        
        self._lib.verify_vc_ffi.argtypes = [ctypes.c_char_p]
        self._lib.verify_vc_ffi.restype = ctypes.c_bool
        
        self._lib.issue_vc_ffi.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self._lib.issue_vc_ffi.restype = ctypes.c_char_p
        
        self._lib.free_string.argtypes = [ctypes.c_char_p]
        self._lib.free_string.restype = None
    
    def generate_did(self, method='key'):
        """
        Generate a new DID using the specified method.
        
        Args:
            method: DID method (default: 'key')
            
        Returns:
            str: Generated DID
        """
        method_bytes = method.encode('utf-8')
        result = self._lib.generate_did_ffi(method_bytes)
        if result:
            did = ctypes.c_char_p(result).value.decode('utf-8')
            self._lib.free_string(result)
            return did
        return None
    
    def verify_vc(self, vc_json):
        """
        Verify a Verifiable Credential.
        
        Args:
            vc_json: Verifiable Credential as JSON string
            
        Returns:
            bool: True if valid, False otherwise
        """
        if isinstance(vc_json, dict):
            vc_json = json.dumps(vc_json)
        vc_bytes = vc_json.encode('utf-8')
        return self._lib.verify_vc_ffi(vc_bytes)
    
    def issue_vc(self, credential, did, private_key):
        """
        Issue a new Verifiable Credential.
        
        Args:
            credential: Credential subject as JSON string
            did: DID of the issuer
            private_key: Private key for signing
            
        Returns:
            str: Issued VC as JSON string or None on error
        """
        if isinstance(credential, dict):
            credential = json.dumps(credential)
        
        cred_bytes = credential.encode('utf-8')
        did_bytes = did.encode('utf-8')
        key_bytes = private_key.encode('utf-8')
        
        result = self._lib.issue_vc_ffi(cred_bytes, did_bytes, key_bytes)
        if result:
            vc = ctypes.c_char_p(result).value.decode('utf-8')
            self._lib.free_string(result)
            return vc
        return None


# Singleton instance
_msgpack = DIDRustWrapper()


def get_wrapper():
    """Get the singleton wrapper instance."""
    return _msgpack


# Convenience functions
def generate_did(method='key'):
    """Generate a DID."""
    return _msgpack.generate_did(method)


def verify_vc(vc_json):
    """Verify a VC."""
    return _msgpack.verify_vc(vc_json)


def issue_vc(credential, did, private_key):
    """Issue a VC."""
    return _msgpack.issue_vc(credential, did, private_key)


# Python fallback implementation
class PythonDIDFallback:
    """Python fallback implementation for DID operations."""
    
    @staticmethod
    def generate_did(method='key'):
        import time
        import random
        timestamp = int(time.time() * 1000)
        rand_suffix = random.randint(1000, 9999)
        return f"did:{method}:python-{timestamp}-{rand_suffix}"
    
    @staticmethod
    def verify_vc(vc_json):
        if isinstance(vc_json, dict):
            vc = vc_json
        else:
            try:
                vc = json.loads(vc_json)
            except:
                return False
        return 'credentialSubject' in vc and 'issuer' in vc
    
    @staticmethod
    def issue_vc(credential, did, private_key):
        if isinstance(credential, dict):
            cred = credential
        else:
            try:
                cred = json.loads(credential)
            except:
                cred = {}
        return json.dumps({
            'vc': cred,
            'issuer': did,
            'issued': True,
            'signature': 'mock-signature'
        })


def get_did_backend():
    """
    Get the appropriate DID backend based on settings.
    Returns Rust wrapper if available and configured, otherwise Python fallback.
    """
    backend = getattr(settings, 'DID_BACKEND', 'rust')
    
    if backend == 'python' or backend is False:
        return PythonDIDFallback()
    
    try:
        return get_wrapper()
    except:
        return PythonDIDFallback()
