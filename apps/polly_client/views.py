"""
Views for Polly Client app - serve Polly polls and handle voting.
"""
import json
import logging
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .client import get_polly_client

logger = logging.getLogger(__name__)


def polls_view(request):
    """View to display list of polls from Polly."""
    user_did = getattr(request.user, 'did', None)
    theme = 'dark' if request.COOKIES.get('theme') == 'dark' else 'light'

    client = get_polly_client()
    polls = client.get_polls(user_did=user_did, theme=theme)

    return render(request, 'polly_client/polls.html', {
        'polls': polls,
        'theme': theme,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def poll_detail_view(request, poll_id):
    """View to display a single poll from Polly."""
    user_did = getattr(request.user, 'did', None)
    theme = 'dark' if request.COOKIES.get('theme') == 'dark' else 'light'

    client = get_polly_client()
    poll = client.get_poll(poll_id, user_did=user_did, theme=theme)

    if not poll:
        return render(request, 'polly_client/poll_not_found.html', {
            'poll_id': poll_id,
            'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
        })

    return render(request, 'polly_client/poll_detail.html', {
        'poll': poll,
        'theme': theme,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@require_http_methods(["GET"])
def api_polls(request):
    """API endpoint to fetch polls for embedding."""
    user_did = request.GET.get('user_did', '')
    theme = request.GET.get('theme', 'light')

    client = get_polly_client()
    polls = client.get_polls(user_did=user_did or None, theme=theme)

    return JsonResponse({
        'polls': polls,
        'theme': theme,
        'embedding_app': client.embedding_app,
    })


@require_http_methods(["GET"])
def api_poll_detail(request, poll_id):
    """API endpoint to fetch a single poll."""
    user_did = request.GET.get('user_did', '')
    theme = request.GET.get('theme', 'light')

    client = get_polly_client()
    poll = client.get_poll(poll_id, user_did=user_did or None, theme=theme)

    if not poll:
        return JsonResponse({'error': 'Poll not found'}, status=404)

    return JsonResponse({
        'poll': poll,
        'theme': theme,
        'user_did': user_did,
    })


@login_required
@require_http_methods(["POST"])
def api_vote(request):
    """API endpoint to submit a vote."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    poll_id = data.get('poll_id')
    option_id = data.get('option_id')
    user_did = getattr(request.user, 'did', None)

    if not user_did:
        return JsonResponse({'error': 'DID required for voting'}, status=401)

    if not poll_id or not option_id:
        return JsonResponse({'error': 'Missing poll_id or option_id'}, status=400)

    # In a full implementation, we'd get the signature from the client
    # For now, we'll just forward to Polly
    signature = data.get('signature', '')

    client = get_polly_client()
    result = client.vote(poll_id, option_id, user_did, signature)

    return JsonResponse(result)


@require_http_methods(["GET"])
def api_health(request):
    """Health check endpoint for Polly connection."""
    client = get_polly_client()
    connected = client.check_connection()

    return JsonResponse({
        'status': 'ok' if connected else 'error',
        'polly_connected': connected,
        'polly_url': client.base_url,
    })