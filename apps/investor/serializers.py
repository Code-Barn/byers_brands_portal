"""
Django REST Framework serializers for Investor app.
"""
from rest_framework import serializers
from .models import Investment, Portfolio, Document, InvestmentOpportunity


class InvestmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Investment
        fields = [
            'id', 'user', 'name', 'amount', 'current_value',
            'date_invested', 'returns_percentage', 'status',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PortfolioSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    investments = InvestmentSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'total_value', 'total_invested',
            'total_returns', 'last_updated', 'investments'
        ]
        read_only_fields = ['id', 'user', 'last_updated']


class DocumentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'user', 'title', 'file', 'file_url',
            'document_type', 'description', 'file_size',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'user', 'file_size', 'uploaded_at']

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class InvestmentOpportunitySerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentOpportunity
        fields = [
            'id', 'title', 'description', 'min_investment',
            'max_investment', 'expected_returns_percentage',
            'status', 'deadline', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortfolioSummarySerializer(serializers.Serializer):
    """Serializer for portfolio summary statistics."""
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_invested = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_returns = serializers.DecimalField(max_digits=12, decimal_places=2)
    returns_percentage = serializers.FloatField()
    investment_count = serializers.IntegerField()
    active_investments = serializers.IntegerField()