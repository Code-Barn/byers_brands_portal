"""
Views for Feedback app.
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .models import Feedback, FeedbackCategory


@login_required
def feedback_form(request):
    """Show feedback submission form."""
    if request.method == 'POST':
        return submit_feedback(request)

    return render(request, 'feedback/submit.html', {
        'categories': FeedbackCategory.choices,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
@csrf_protect
def submit_feedback(request):
    """Handle feedback submission via POST or AJAX."""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        category = request.POST.get('category', FeedbackCategory.SUGGESTION)
        screenshot = request.FILES.get('screenshot')

        if not subject or not message:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Subject and message are required'}, status=400)
            messages.error(request, 'Please provide both subject and message.')
            return redirect('feedback:submit')

        feedback = Feedback.objects.create(
            user=request.user,
            subject=subject,
            message=message,
            category=category,
            screenshot=screenshot,
            url_context=request.META.get('HTTP_REFERER', '')
        )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your feedback!'
            })

        messages.success(request, 'Thank you for your feedback! We appreciate your input.')
        return redirect('feedback:submit')

    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def feedback_success(request):
    """Show feedback submission success page."""
    return render(request, 'feedback/success.html', {
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def feedback_list(request):
    """List all feedback (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('brand:home')

    feedbacks = Feedback.objects.all()[:50]
    return render(request, 'feedback/list.html', {
        'feedbacks': feedbacks,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def feedback_detail(request, feedback_id):
    """Show feedback detail (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('brand:home')

    feedback = get_object_or_404(Feedback, id=feedback_id)
    return render(request, 'feedback/detail.html', {
        'feedback': feedback,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@require_http_methods(["POST"])
@login_required
def feedback_update_status(request, feedback_id):
    """Update feedback status (admin only)."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    feedback = get_object_or_404(Feedback, id=feedback_id)
    status = request.POST.get('status')

    if status in dict(Feedback.FeedbackStatus.choices):
        feedback.status = status
        feedback.save()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid status'}, status=400)