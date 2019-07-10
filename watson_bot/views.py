import json
import requests, random, re
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# For logging requests
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# In a real project this would probably not be commited to repo.
VERIFY_TKN = "d1d892cade69e4dc000b6db0d55d93ea734587e04b01bd0c7a" # TODO: Place in config file
PAGE_ACCESS_TOKEN = ("EAAGGuYZBs8B4BANuAW3Vf0GqDO2xxLZAmRZAls10opZCCTyYkIxD8MW"
    + "GjAjkuxQtYjVVgTChQs4jYKjCm6LCOl2w3PH7OZChiD71wAyfx3hHzYHwGyDzn6qhu78FAUrkiL"
    + "y3RtgLm3ETLXkrvurVqMY1ZAhZCv6DLngiTZBEx0aW1QZDZD")
FACEBOOK_ENDPOINT = "https://graph.facebook.com/v2.6/me/messages"

def send_message(recipient_id, recieved_message):
    endpoint = f"{FACEBOOK_ENDPOINT}/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    msg = "TEST MESSAGE"
    payload = json.dumps(
        {"recipient":{"id": recipient_id}, "message":{"text": msg}})

    status = requests.post(
        endpoint, 
        headers={"Content-Type": "application/json"},
        data=payload)
    return status.json()


class FacebookWebhookVew(View):
    @staticmethod
    def log(request, data):
        logging.getLogger("djangosyslog").info(request)
        logging.getLogger("djangosyslog").info(data)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        FacebookWebhookVew.log(request, data)
        return HttpResponse("Request returned")

    def get(self, request, *args, **kwargs):
        FacebookWebhookVew.log(request, None)
        return HttpResponse(request.GET.get('hub.challenge'))

class DjangoRunsView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, requuest, *args, **kwargs):
        return HttpResponse("App is live.")