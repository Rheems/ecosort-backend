from rest_framework import serializers
from .models import PaymentAccount, Payment


class PaymentAccountSerializer(serializers.ModelSerializer):
    masked_account = serializers.SerializerMethodField()

    class Meta:
        model = PaymentAccount
        fields = [
            "id",
            "bank_name",
            "bank_code",
            "account_name",
            "masked_account",
            "verification_status",
            "is_primary",
            "created_at",
        ]

    def get_masked_account(self, obj):
        num = obj.account_number
        return f"{num[:4]}****{num[-4:]}" if len(num) == 10 else num


class BankAccountInputSerializer(serializers.Serializer):
    bank_code = serializers.CharField(max_length=10)
    account_number = serializers.CharField(min_length=10, max_length=10)

    def validate_account_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Account number must be 10 digits, numeric only."
            )
        return value


class PaymentSerializer(serializers.ModelSerializer):
    collector_name = serializers.SerializerMethodField()
    household_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "collector_name",
            "household_name",
            "amount",
            "currency",
            "payment_status",
            "provider_reference",
            "failure_reason",
            "retry_count",
            "initiated_at",
            "completed_at",
        ]

    def get_collector_name(self, obj):
        return obj.collector.get_full_name() or obj.collector.username

    def get_household_name(self, obj):
        name = obj.household.get_full_name() or obj.household.username
        # Mask surname for privacy
        parts = name.split()
        if len(parts) > 1:
            return f"{parts[0]} {parts[-1][:2]}."
        return name


class InitiatePaymentSerializer(serializers.Serializer):
    pickup_id = serializers.IntegerField()
    household_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)