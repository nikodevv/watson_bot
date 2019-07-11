import json
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import time
from watson_bot.models import Session, Message
from watson_bot.env import (
    FB_VERIFY_TKN, 
    FB_PAGE_ACCESS_TOKEN, 
    WATSON_PASSWORD, 
    WATSON_USERNAME
    )

# CONFIG
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# CONSTANTS
FACEBOOK_ENDPOINT = "https://graph.facebook.com/v2.6/me/messages"
WATSON_ENDPOINT = ("https://gateway.watsonplatform.net/assistant/api/v2/" 
    + "assistants/11c98e51-0aab-4455-a0bd-b64ffe723145/sessions")
WATSON_API_VER = "version=2019-02-28"


# UTILITY FUNCTIONS
def send_message(recipient_id, recieved_message):
    endpoint = f"{FACEBOOK_ENDPOINT}/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    msg = "TEST MESSAGE"
    payload = json.dumps(
        {"recipient":{"id": recipient_id}, "message":{"text": msg}})

    status = requests.post(
        endpoint, 
        headers={"Content-Type": "application/json"},
        data=payload)
    return status.json()

class FacebookWebhookView(View):
    @staticmethod
    def log(request):
        logging.getLogger("djangosyslog").info(request)

    @staticmethod
    def create_watson_session():
        session = requests.Session()
        session.auth = (WATSON_USERNAME, WATSON_PASSWORD)
        print(session.post(f'{WATSON_ENDPOINT}?{WATSON_API_VER}').content)

    @staticmethod
    def save_session(session_id):
        timestamp = time.time()

        session = Session()
        session.id = session_id
        session.created_at = timestamp
        session.last_updated = timestamp
        session.save()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        FacebookWebhookView.log(request)
        FacebookWebhookView.create_watson_session()
        return HttpResponse("EVENT_RECIEVED")

    def get(self, request, *args, **kwargs):
        FacebookWebhookView.log(request)
        return HttpResponse(request.GET.get('hub.challenge'))

class DjangoRunsView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, requuest, *args, **kwargs):
        return HttpResponse("App is live.")