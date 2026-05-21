from django.http import JsonResponse
from .services.africastalking_service import sms


# Create your views here.
def test_sms(request):
    if request.method == 'POST':
        # Example SMS sending logic
        try:
            response = sms.send(
                message="Africa Talking integration succesful!",
                recipients=["+254712345678"]
            )
            return JsonResponse({'status': 'success', 'data': response})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})