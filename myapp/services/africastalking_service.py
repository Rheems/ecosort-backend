import africastalking
from django.conf import settings

africastalking.initialize(
    settings.AT_USERNAME, 
    settings.AT_API_KEY
    )

sms = africastalking.SMS