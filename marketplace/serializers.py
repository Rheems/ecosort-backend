from rest_framework import serializers
from .models import MaterialListing, MarketplaceTransaction, PricingReference


class PricingReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingReference
        fields = [
            'material_type',
            'min_price_per_kg',
            'max_price_per_kg',
            'suggested_price_per_kg',
            'last_updated',
            'source',
        ]


class MaterialListingSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = MaterialListing
        fields = [
            'id',
            'seller_name',
            'material_type',
            'quantity_kg',
            'price_per_kg',
            'total_price',
            'location',
            'description',
            'status',
            'channel',
            'expires_at',
            'is_expired',
            'created_at',
        ]
        read_only_fields = ['total_price', 'seller_name', 'is_expired']

    def get_is_expired(self, obj):
        return obj.is_expired()


class CreateListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialListing
        fields = [
            'material_type',
            'quantity_kg',
            'price_per_kg',
            'location',
            'description',
        ]


class MarketplaceTransactionSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    listing_material = serializers.CharField(source='listing.material_type', read_only=True)
    seller_name = serializers.CharField(source='listing.seller.username', read_only=True)

    class Meta:
        model = MarketplaceTransaction
        fields = [
            'id',
            'buyer_name',
            'seller_name',
            'listing_material',
            'quantity_kg',
            'total_paid',
            'status',
            'created_at',
        ]