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
    WATSON_USERNAME,
    WATSON_FB_ID
    )

# CONFIG
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# CONSTANTS
FACEBOOK_ENDPOINT = "https://graph.facebook.com/v2.6/me/messages"
WATSON_ENDPOINT = ("https://gateway.watsonplatform.net/assistant/api/v2/" 
    + "assistants/11c98e51-0aab-4455-a0bd-b64ffe723145/sessions")
WATSON_API_VER = "version=2019-02-28"
SESSION_TIMEOUT = 5*60 - 10 # Session timeout after this long


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
    def log(self, request):
        logging.getLogger("djangosyslog").info(request)

    def create_watson_session(self):
        session = requests.Session()
        session.auth = (WATSON_USERNAME, WATSON_PASSWORD)
        print(session.post(f'{WATSON_ENDPOINT}?{WATSON_API_VER}').content)

    def save_session(self, session_id):
        timestamp = time.time()

        session = Session()
        session.session_id = session_id
        session.created_at = timestamp
        session.last_renewed = timestamp
        session.save()
        return session

    def renew_session(self, session_id):
        timestamp = time.time()
        session = Session.objects.get(pk=session_id)
        session.last_renewed = timestamp
        session.save()

    def should_renew_session(self, session):
        return session.last_renewed + SESSION_TIMEOUT < time.time()


    def should_create_message(self, facebook_entry):
        for indx, obj in enumerate(facebook_entry["messaging"]):
            if "sender" in obj and obj["sender"] == WATSON_FB_ID:
                # if the sender is the bot messages are saved when they are sent
                # not received
                return False
        return True

    def create_session(self):
        session = requests.Session()
        session.auth = (WATSON_USERNAME, WATSON_PASSWORD)
        return session.post(f'{WATSON_ENDPOINT}?{WATSON_API_VER}')

    def get_sender_id(self, facebook_entry):
        for obj in facebook_entry["messaging"]:
            if "sender" in obj:
                return obj["sender"]["id"]

    def create_message(self, facebook_entry):
        min_timestamp_before_timeout = time.time() - SESSION_TIMEOUT
        sender_id = get_sender_id(facebook_entry)

        recent_msgs = Message.objects.filter(
            timestamp__gt=min_timestamp_before_timeout,
            sender_id__exact=sender_id)

        if (len(recent_msgs) == 0):
            # Create new session
            session_id = json.loads(self.create_session().content.decode('utf-8'))["session_id"]
            session = self.save_session(session_id)

        elif (not self.should_renew_session(recent_msgs[0].session)):
            # Create new session
            session_id = json.loads(self.create_session().content.decode('utf-8'))["session_id"]
            session = self.save_session(session_id)
        
        else: 
            session = recent_msgs[0].session
            self.renew_session(session.id)

        self.save_message(facebook_entry, session)


    def save_message(self, facebook_entry, session):
        pass

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        self.log(request)
        self.create_watson_session()
        return HttpResponse("EVENT_RECIEVED")

    def get(self, request, *args, **kwargs):
        self.log(request)
        return HttpResponse(request.GET.get('hub.challenge'))

class DjangoRunsView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, requuest, *args, **kwargs):
        return HttpResponse("App is live.")