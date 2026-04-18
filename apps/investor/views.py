"""
Views for Investor app - portfolio, documents, opportunities, and API.
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Investment, Portfolio, Document, InvestmentOpportunity
from .serializers import (
    InvestmentSerializer,
    PortfolioSerializer,
    DocumentSerializer,
    InvestmentOpportunitySerializer,
    PortfolioSummarySerializer
)

User = get_user_model()


@login_required
def investor_dashboard(request):
    """Main investor dashboard view."""
    user = request.user

    portfolio = Portfolio.objects.filter(user=user).first()
    investments = Investment.objects.filter(user=user)[:5]
    documents = Document.objects.filter(user=user)[:5]
    opportunities = InvestmentOpportunity.objects.filter(
        status=InvestmentOpportunity.OpportunityStatus.AVAILABLE
    )[:6]

    return render(request, 'investor/dashboard.html', {
        'user': user,
        'portfolio': portfolio,
        'investments': investments,
        'documents': documents,
        'opportunities': opportunities,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def portfolio_view(request):
    """Full portfolio view with all investments."""
    user = request.user
    portfolio = Portfolio.objects.filter(user=user).first()
    investments = Investment.objects.filter(user=user).order_by('-created_at')

    return render(request, 'investor/portfolio.html', {
        'portfolio': portfolio,
        'investments': investments,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def documents_view(request):
    """Document management view."""
    user = request.user
    documents = Document.objects.filter(user=user).order_by('-uploaded_at')

    return render(request, 'investor/documents.html', {
        'documents': documents,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
def opportunities_view(request):
    """Investment opportunities listing."""
    opportunities = InvestmentOpportunity.objects.filter(
        status=InvestmentOpportunity.OpportunityStatus.AVAILABLE
    ).order_by('-created_at')

    return render(request, 'investor/opportunities.html', {
        'opportunities': opportunities,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


@login_required
@csrf_protect
def upload_document(request):
    """Handle document upload."""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        document_type = request.POST.get('document_type', 'other')
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return JsonResponse({'error': 'File too large (max 10MB)'}, status=400)

        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif',
                        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if uploaded_file.content_type not in allowed_types:
            return JsonResponse({'error': 'Invalid file type'}, status=400)

        document = Document.objects.create(
            user=request.user,
            title=title or uploaded_file.name,
            file=uploaded_file,
            document_type=document_type,
            description=description,
            file_size=uploaded_file.size
        )

        return JsonResponse({
            'id': document.id,
            'title': document.title,
            'file_url': document.file.url
        })

    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def download_document(request, document_id):
    """Download a document."""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    return HttpResponse(document.file, content_type='application/octet-stream')


@login_required
def delete_document(request, document_id):
    """Delete a document."""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    document.file.delete()
    document.delete()
    return JsonResponse({'success': True})


@login_required
def roi_calculator(request):
    """ROI Calculator view."""
    return render(request, 'investor/roi_calculator.html', {
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


# API Views for REST endpoints

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_investments(request):
    """API endpoint for investments."""
    if request.method == 'GET':
        investments = Investment.objects.filter(user=request.user)
        serializer = InvestmentSerializer(investments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = InvestmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            portfolio = Portfolio.objects.filter(user=request.user).first()
            if portfolio:
                portfolio.update_totals()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_portfolio(request):
    """API endpoint for portfolio."""
    if request.method == 'GET':
        portfolio, created = Portfolio.objects.get_or_create(user=request.user)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)

    elif request.method == 'POST':
        portfolio, created = Portfolio.objects.get_or_create(user=request.user)
        portfolio.update_totals()
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_portfolio_summary(request):
    """API endpoint for portfolio summary statistics."""
    portfolio, created = Portfolio.objects.get_or_create(user=request.user)
    portfolio.update_totals()

    investments = Investment.objects.filter(user=request.user)
    active_investments = investments.filter(status='active')

    summary = {
        'total_value': portfolio.total_value,
        'total_invested': portfolio.total_invested,
        'total_returns': portfolio.total_returns,
        'returns_percentage': (portfolio.total_returns / portfolio.total_invested * 100) if portfolio.total_invested > 0 else 0,
        'investment_count': investments.count(),
        'active_investments': active_investments.count()
    }
    serializer = PortfolioSummarySerializer(summary)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_documents(request):
    """API endpoint for documents."""
    if request.method == 'GET':
        documents = Document.objects.filter(user=request.user)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=400)

        max_size = 10 * 1024 * 1024
        if uploaded_file.size > max_size:
            return Response({'error': 'File too large (max 10MB)'}, status=400)

        document = Document.objects.create(
            user=request.user,
            title=request.data.get('title', uploaded_file.name),
            file=uploaded_file,
            document_type=request.data.get('document_type', 'other'),
            description=request.data.get('description', ''),
            file_size=uploaded_file.size
        )
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_opportunities(request):
    """API endpoint for investment opportunities."""
    opportunities = InvestmentOpportunity.objects.filter(
        status=InvestmentOpportunity.OpportunityStatus.AVAILABLE
    )
    serializer = InvestmentOpportunitySerializer(opportunities, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_document(request, document_id):
    """API endpoint to delete a document."""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    document.file.delete()
    document.delete()
    return Response({'success': True})