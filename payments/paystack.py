import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"

headers = {
    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}


def get_banks():
    """Fetch list of Nigerian banks from Paystack"""
    response = requests.get(f"{PAYSTACK_BASE_URL}/bank", headers=headers)
    return response.json()


def verify_account(account_number, bank_code):
    """Resolve bank account name via Paystack"""
    url = f"{PAYSTACK_BASE_URL}/bank/resolve"
    params = {
        "account_number": account_number,
        "bank_code": bank_code,
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def initiate_transfer(amount, recipient_code, reason="Ecosort Payment"):
    """Send money to a recipient"""
    url = f"{PAYSTACK_BASE_URL}/transfer"
    payload = {
        "source": "balance",
        "amount": int(amount * 100),  # Paystack uses kobo
        "recipient": recipient_code,
        "reason": reason,
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def create_transfer_recipient(account_name, account_number, bank_code):
    """Register a bank account as a transfer recipient on Paystack"""
    url = f"{PAYSTACK_BASE_URL}/transferrecipient"
    payload = {
        "type": "nuban",
        "name": account_name,
        "account_number": account_number,
        "bank_code": bank_code,
        "currency": "NGN",
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()