"""
Audit logging middleware for capturing DID operations.
"""
import json
import threading

_audit_log_queue = []
_audit_log_lock = threading.Lock()


class AuditLogMiddleware:
    """
    Middleware to capture and log authentication-related events.
    Logs are stored in a thread-local queue and flushed to the database.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_request(self, request):
        """Capture request metadata for audit logging."""
        request._audit_log_data = {
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
        }
        return None

    def process_response(self, request, response):
        """Log authentication-related responses."""
        if self._should_log(request):
            self._log_request(request, response)
        return response

    def _should_log(self, request):
        """Determine if request should be logged."""
        auth_paths = [
            '/accounts/login/',
            '/accounts/did-login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/accounts/api/',
            '/investor/',
            '/admin/',
        ]
        path = request.path
        return any(path.startswith(p) for p in auth_paths)

    def _log_request(self, request, response):
        """Log the authentication request."""
        from .audit_models import AuditLog

        action = None
        details = ''

        if request.path == '/accounts/login/' and request.method == 'POST':
            action = AuditLog.ActionType.LOGIN if response.status_code == 302 else AuditLog.ActionType.LOGIN_FAILED
            details = f"Email login attempt: {request.POST.get('email', 'unknown')}"

        elif request.path == '/accounts/did-login/' and request.method == 'POST':
            action = AuditLog.ActionType.DID_LOGIN if response.status_code == 302 else AuditLog.ActionType.DID_LOGIN_FAILED
            did = request.POST.get('did', 'unknown')
            details = f"DID login attempt: {did[:30]}..."

        elif request.path == '/accounts/logout/':
            action = AuditLog.ActionType.LOGOUT
            details = "User logged out"

        elif request.path == '/accounts/register/' and request.method == 'POST':
            action = AuditLog.ActionType.REGISTER
            details = f"Registration attempt: {request.POST.get('email', 'unknown')}"

        elif '/api/' in request.path:
            if 'challenge' in request.path:
                action = AuditLog.ActionType.DID_GENERATED
                details = "DID authentication challenge generated"
            elif 'verify-vc' in request.path:
                action = AuditLog.ActionType.VC_VERIFIED
                details = "Verifiable credential verification attempted"

        if action:
            user = getattr(request, 'user', None)
            user_did = getattr(user, 'did', None) if user and user.is_authenticated else None

            AuditLog.log_action(
                user=user if user and user.is_authenticated else None,
                user_did=user_did,
                action=action,
                action_details=details,
                metadata={'status_code': response.status_code},
                request=request
            )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class DIDOperationLogger:
    """
    Utility class for logging DID-specific operations.
    Used by views and serializers for explicit operation logging.
    """

    @staticmethod
    def log_vc_issuance(user, did, vc_id, credential_type):
        """Log VC issuance."""
        from .audit_models import AuditLog
        AuditLog.log_action(
            user=user,
            user_did=did,
            action=AuditLog.ActionType.VC_ISSUED,
            action_details=f"Issued {credential_type} credential",
            metadata={'vc_id': str(vc_id)}
        )

    @staticmethod
    def log_vc_verification(user, did, vc_id, success):
        """Log VC verification attempt."""
        from .audit_models import AuditLog
        action = AuditLog.ActionType.VC_VERIFIED if success else AuditLog.ActionType.VC_VERIFICATION_FAILED
        AuditLog.log_action(
            user=user,
            user_did=did,
            action=action,
            action_details=f"VC verification: {'success' if success else 'failed'}",
            metadata={'vc_id': str(vc_id) if vc_id else None}
        )

    @staticmethod
    def log_mfa_action(user, action_type, success=True):
        """Log MFA-related actions."""
        from .audit_models import AuditLog
        action = action_type
        if not success:
            action = action_type.replace('_verified', '_verification_failed')
        AuditLog.log_action(
            user=user,
            user_did=user.did if user else None,
            action=action,
            action_details=f"MFA action: {action_type}"
        )