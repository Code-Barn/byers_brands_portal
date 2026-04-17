"""
Views for user authentication and DID-based login.
"""
import json
import secrets
import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, DIDLoginForm
from .did_rust_wrapper import get_did_backend, generate_did

CustomUser = get_user_model()

# In-memory challenge store (replace with cache in production)
_challenges = {}


def home(request):
    """Redirect to brand home or investor dashboard if authenticated."""
    if request.user.is_authenticated:
        if request.path == '/accounts/' or request.path == '/accounts':
            return redirect('brand:home')
    return redirect('brand:home')


@csrf_protect
def register(request):
    """User registration with optional DID generation."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Generate DID for the user
            try:
                did_backend = get_did_backend()
                did = did_backend.generate_did('key')
                user.did = did
                user.did_document = {
                    'id': did,
                    'type': 'DIDDocument',
                    'method': 'key'
                }
            except Exception as e:
                print(f"Failed to generate DID: {e}")
                messages.warning(request, 'DID generation skipped - Rust library not available')
            
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@csrf_protect
def user_login(request):
    """User login view."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'brand:home')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def user_logout(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('brand:home')


def generate_challenge(request):
    """Generate a challenge for DID authentication."""
    challenge = secrets.token_hex(32)
    session_id = request.session.session_key or secrets.token_hex(16)
    _challenges[session_id] = challenge
    
    if not request.session.session_key:
        request.session.create()
    
    return JsonResponse({
        'challenge': challenge,
        'session_id': request.session.session_key
    })


@csrf_protect
def did_login(request):
    """DID-based login view."""
    if request.method == 'POST':
        form = DIDLoginForm(request.POST)
        if form.is_valid():
            did = form.cleaned_data['did']
            proof = form.cleaned_data['proof']
            
            # Verify proof (simplified - in production, verify the signature)
            try:
                session_id = request.session.session_key
                challenge = _challenges.get(session_id, '')
                
                if not challenge:
                    messages.error(request, 'Invalid or expired challenge')
                    return render(request, 'accounts/did_login.html', {'form': form})
                
                # Try to find user with this DID
                user = CustomUser.objects.filter(did=did).first()
                
                if user:
                    # Authenticate user (bypass password in this flow)
                    # In production, properly verify the proof
                    login(request, user)
                    messages.success(request, f'Welcome back, DID user!')
                    del _challenges[session_id]
                    return redirect('brand:home')
                else:
                    # Create new user with DID
                    username = f"did_{did[-8:]}"
                    user = CustomUser.objects.create_user(
                        email=f"{did}@did.local",
                        username=username,
                        did=did,
                        did_document={'id': did, 'type': 'DIDDocument'}
                    )
                    login(request, user)
                    messages.success(request, 'New DID account created and logged in!')
                    del _challenges[session_id]
                    return redirect('brand:home')
                    
            except Exception as e:
                messages.error(request, f'Authentication failed: {e}')
    else:
        form = DIDLoginForm()
    
    return render(request, 'accounts/did_login.html', {
        'form': form,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def profile(request):
    """User profile view."""
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def investor_dashboard(request):
    """Investor dashboard placeholder."""
    return render(request, 'accounts/investor_dashboard.html', {
        'user': request.user,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


# API Views for DID operations
def api_generate_did(request):
    """API endpoint to generate a DID."""
    try:
        did = generate_did('key')
        return JsonResponse({'did': did})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_verify_vc(request):
    """API endpoint to verify a Verifiable Credential."""
    if request.method == 'POST':
        try:
            vc = json.loads(request.body)
            did_backend = get_did_backend()
            valid = did_backend.verify_vc(vc)
            return JsonResponse({'valid': valid})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)
