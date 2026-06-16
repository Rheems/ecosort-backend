from django.urls import path
from . import views

urlpatterns = [
    # Bank setup
    path("banks/", views.get_banks, name="get-banks"),
    path("verify-account/", views.verify_account, name="verify-account"),
    path("bank-account/", views.save_bank_account, name="save-bank-account"),
    path("bank-account/me/", views.get_bank_account, name="get-bank-account"),
    path("bank-account/remove/", views.remove_bank_account, name="remove-bank-account"),

    # Payments
    path("initiate/", views.initiate_payment, name="initiate-payment"),
    path("retry/<int:payment_id>/", views.retry_payment, name="retry-payment"),
    path("my-payments/", views.my_payments, name="my-payments"),

    # Webhook
    path("webhook/paystack/", views.paystack_webhook, name="paystack-webhook"),
]