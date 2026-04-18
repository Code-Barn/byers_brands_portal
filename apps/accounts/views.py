"""
Views for user authentication and DID-based login.
"""
import json
import secrets
import os
import pyotp
import qrcode
import io
import base64
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, DIDLoginForm
from .did_rust_wrapper import get_did_backend, generate_did, create_challenge
from .audit_models import AuditLog

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

            # Audit log
            AuditLog.log_action(
                user=user,
                user_did=user.did,
                action=AuditLog.ActionType.REGISTER,
                action_details='New user registered',
                metadata={'email': user.email},
                request=request
            )

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
    """User login view with optional MFA."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Check if MFA is enabled
            if user.mfa_enabled:
                # Store user in session for MFA verification
                request.session['pre_mfa_user_id'] = user.id
                request.session['mfa_required'] = True
                return redirect('accounts:mfa_verify')

            # Normal login (no MFA)
            login(request, user)

            # Audit log
            AuditLog.log_action(
                user=user,
                user_did=user.did,
                action=AuditLog.ActionType.LOGIN,
                action_details='User logged in with email/password',
                request=request
            )

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
    user = request.user if request.user.is_authenticated else None
    logout(request)

    if user:
        AuditLog.log_action(
            user=user,
            user_did=getattr(user, 'did', None),
            action=AuditLog.ActionType.LOGOUT,
            action_details='User logged out',
            request=request
        )

    messages.info(request, 'You have been logged out.')
    return redirect('brand:home')


def generate_challenge(request):
    """Generate a challenge for DID authentication."""
    challenge = create_challenge()
    session_id = request.session.session_key or secrets.token_hex(16)
    _challenges[session_id] = challenge

    if not request.session.session_key:
        request.session.create()

    # Audit log for challenge generation
    AuditLog.log_action(
        action=AuditLog.ActionType.DID_GENERATED,
        action_details='DID authentication challenge generated',
        request=request
    )

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
                    # Check if MFA is enabled for this user
                    if user.mfa_enabled:
                        request.session['pre_mfa_user_id'] = user.id
                        request.session['mfa_required'] = True
                        request.session['mfa_did'] = did
                        del _challenges[session_id]
                        return redirect('accounts:mfa_verify')

                    # Authenticate user (bypass password in this flow)
                    login(request, user)

                    # Audit log
                    AuditLog.log_action(
                        user=user,
                        user_did=did,
                        action=AuditLog.ActionType.DID_LOGIN,
                        action_details='User logged in with DID',
                        request=request
                    )

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

                    # Audit log
                    AuditLog.log_action(
                        user=user,
                        user_did=did,
                        action=AuditLog.ActionType.DID_LOGIN,
                        action_details='New user created via DID login',
                        request=request
                    )

                    login(request, user)
                    messages.success(request, 'New DID account created and logged in!')
                    del _challenges[session_id]
                    return redirect('brand:home')

            except Exception as e:
                # Audit log for failed login
                AuditLog.log_action(
                    user_did=did,
                    action=AuditLog.ActionType.DID_LOGIN_FAILED,
                    action_details=f'DID login failed: {str(e)}',
                    request=request
                )
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
    """Redirect to the new investor dashboard."""
    return redirect('investor:dashboard')


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

            # Audit log
            AuditLog.log_action(
                action=AuditLog.ActionType.VC_VERIFIED if valid else AuditLog.ActionType.VC_VERIFICATION_FAILED,
                action_details=f'VC verification: {"success" if valid else "failed"}',
                request=request
            )

            return JsonResponse({'valid': valid})
        except Exception as e:
            AuditLog.log_action(
                action=AuditLog.ActionType.VC_VERIFICATION_FAILED,
                action_details=f'VC verification error: {str(e)}',
                request=request
            )
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)


# MFA Views

@login_required
def mfa_setup(request):
    """Setup MFA for the current user."""
    user = request.user

    if user.mfa_enabled:
        messages.info(request, 'MFA is already enabled for your account.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        # Generate and save MFA secret
        secret = user.generate_mfa_secret()
        user.set_mfa_secret(secret)
        user.save()

        # Audit log
        AuditLog.log_action(
            user=user,
            user_did=user.did,
            action=AuditLog.ActionType.MFA_ENABLED,
            action_details='MFA setup initiated',
            request=request
        )

        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(user.email, issuer_name='Byers Brands')

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render(request, 'accounts/mfa_setup.html', {
            'secret': secret,
            'qr_code': qr_base64,
            'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
        })

    return render(request, 'accounts/mfa_setup_start.html', {
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def mfa_verify_code(request):
    """Verify and enable MFA."""
    user = request.user

    if not user.mfa_secret:
        return redirect('accounts:mfa_setup')

    if request.method == 'POST':
        code = request.POST.get('code', '')
        backup_code = request.POST.get('backup_code', '')

        # Try TOTP first
        if code:
            if user.verify_mfa_code(code):
                # Generate backup codes
                backup_codes = user.generate_backup_codes()
                user.mfa_enabled = True
                user.mfa_last_verified = timezone.now()
                user.save()

                # Audit log
                AuditLog.log_action(
                    user=user,
                    user_did=user.did,
                    action=AuditLog.ActionType.MFA_ENABLED,
                    action_details='MFA enabled successfully',
                    request=request
                )

                messages.success(request, 'MFA has been enabled successfully!')
                messages.info(request, f'Save these backup codes: {", ".join(backup_codes)}')
                return redirect('accounts:profile')
            else:
                # Audit log failed attempt
                AuditLog.log_action(
                    user=user,
                    user_did=user.did,
                    action=AuditLog.ActionType.MFA_VERIFICATION_FAILED,
                    action_details='MFA setup verification failed',
                    request=request
                )
                messages.error(request, 'Invalid verification code. Please try again.')

        # Try backup code
        elif backup_code and user.mfa_backup_codes:
            if backup_code.upper() in user.mfa_backup_codes:
                user.mfa_backup_codes.remove(backup_code.upper())
                user.mfa_enabled = True
                user.mfa_last_verified = timezone.now()
                user.save()

                AuditLog.log_action(
                    user=user,
                    user_did=user.did,
                    action=AuditLog.ActionType.MFA_ENABLED,
                    action_details='MFA enabled via backup code',
                    request=request
                )

                messages.success(request, 'MFA has been enabled successfully!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid backup code.')

    return render(request, 'accounts/mfa_verify.html', {
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def mfa_verify(request):
    """Verify MFA during login."""
    user_id = request.session.get('pre_mfa_user_id')
    did = request.session.get('mfa_did')

    if not user_id:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('accounts:login')

    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, 'User not found.')
        return redirect('accounts:login')

    if request.method == 'POST':
        code = request.POST.get('code', '')
        backup_code = request.POST.get('backup_code', '')

        # Try TOTP first
        if code:
            if user.verify_mfa_code(code):
                # Complete login
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                # Update last verified
                user.mfa_last_verified = timezone.now()
                user.save()

                # Clear session
                request.session.pop('pre_mfa_user_id', None)
                request.session.pop('mfa_required', None)
                request.session.pop('mfa_did', None)

                # Audit log
                AuditLog.log_action(
                    user=user,
                    user_did=user.did or did,
                    action=AuditLog.ActionType.MFA_VERIFIED,
                    action_details='MFA verified during login',
                    request=request
                )

                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('brand:home')
            else:
                AuditLog.log_action(
                    user=user,
                    user_did=user.did or did,
                    action=AuditLog.ActionType.MFA_VERIFICATION_FAILED,
                    action_details='MFA verification failed during login',
                    request=request
                )
                messages.error(request, 'Invalid MFA code. Please try again.')

        # Try backup code
        elif backup_code and user.mfa_backup_codes:
            if backup_code.upper() in user.mfa_backup_codes:
                user.mfa_backup_codes.remove(backup_code.upper())
                user.mfa_last_verified = timezone.now()
                user.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                request.session.pop('pre_mfa_user_id', None)
                request.session.pop('mfa_required', None)
                request.session.pop('mfa_did', None)

                AuditLog.log_action(
                    user=user,
                    user_did=user.did or did,
                    action=AuditLog.ActionType.MFA_BACKUP_USED,
                    action_details='MFA verified via backup code during login',
                    request=request
                )

                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('brand:home')
            else:
                messages.error(request, 'Invalid backup code.')

    return render(request, 'accounts/mfa_login_verify.html', {
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def mfa_disable(request):
    """Disable MFA for the current user."""
    user = request.user

    if not user.mfa_enabled:
        messages.info(request, 'MFA is not enabled for your account.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        # Verify password before disabling
        password = request.POST.get('password', '')
        if not user.check_password(password):
            messages.error(request, 'Incorrect password.')
            return redirect('accounts:mfa_disable')

        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = ''
        user.mfa_secret_hash = ''
        user.mfa_backup_codes = None
        user.save()

        # Audit log
        AuditLog.log_action(
            user=user,
            user_did=user.did,
            action=AuditLog.ActionType.MFA_DISABLED,
            action_details='MFA disabled by user',
            request=request
        )

        messages.success(request, 'MFA has been disabled.')
        return redirect('accounts:profile')

    return render(request, 'accounts/mfa_disable.html', {
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })
