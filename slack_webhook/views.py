from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from slack_sdk.signature import SignatureVerifier


@require_POST
@csrf_exempt
def webhook_view(request):
    verifier = SignatureVerifier(signing_secret=settings.SLACK_SIGNING_SECRET)
    if not verifier.is_valid_request(request.body.decode("utf-8"), request.headers):
        return HttpResponseForbidden()
    return JsonResponse({"text": "Hello from Django!"})
