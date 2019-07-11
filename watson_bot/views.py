import json
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import time
from watson_bot.models import Session, Message, Hobby
from watson_bot.env import (
    FB_VERIFY_TKN, 
    FB_PAGE_ACCESS_TOKEN, 
    WATSON_FB_ID
    )
from watson_bot.utilities.watson_interface import WatsonInterface

# CONSTANTS
FACEBOOK_ENDPOINT = "https://graph.facebook.com/v2.6/me/messages"
SESSION_TIMEOUT = 5*60 - 10 # Session timeout after this long

watson = WatsonInterface()


# UTILITY FUNCTIONS
def send_message(recipient_id, message):
    endpoint = f"{FACEBOOK_ENDPOINT}?access_token={FB_PAGE_ACCESS_TOKEN}"
    payload = json.dumps(
        {
            "messaging_type": "RESPONSE",
            "recipient": { "id": recipient_id },
            "message": { "text": message } 
            }

        )

    status = requests.post(
        endpoint, 
        headers={"Content-Type": "application/json"},
        data=payload)
    print("facebook post")
    print(status.content.decode("utf-8"))
    return status.json()

class FacebookWebhookView(View):

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
        return session.last_renewed + SESSION_TIMEOUT > time.time()


    def should_create_message(self, facebook_entry):
        for indx, obj in enumerate(facebook_entry["messaging"]):
            if "sender" in obj and obj["sender"] == WATSON_FB_ID:
                # if the sender is the bot messages are saved when they are sent
                # not received
                return False
        return True

    def get_sender_id(self, facebook_entry):
        for obj in facebook_entry["messaging"]:
            if "sender" in obj:
                return obj["sender"]["id"]

    def create_message(self, facebook_entry):
        min_timestamp_before_timeout = time.time() - SESSION_TIMEOUT
        sender_id = self.get_sender_id(facebook_entry)

        print("2222222")
        recent_msgs = Message.objects.filter(
            timestamp__gt=min_timestamp_before_timeout,
            sender_id__exact=sender_id)

        print("3333333")
        if (len(recent_msgs) == 0):
            session_id = watson.create_session()["session_id"]
            session = self.save_session(session_id)

        elif (self.should_renew_session(recent_msgs[0].session) == False):
            # Create new session
            session_id = watson.create_session()["session_id"]
            session = self.save_session(session_id)
        
        else: 
            print("CONDITION 3")
            session = recent_msgs[0].session
            self.renew_session(session.session_id)


        print("4444444")
        message = self.save_message(facebook_entry, session)
        watson_response = watson.send_message(message.text, session.session_id)
        self.save_watson_response(watson_response, sender_id)
        send_message(sender_id, watson_response["generic"][0]["text"])


    def save_watson_response(self, watson_response, sender_id):
        for intent in watson_response["intents"]:
            if intent["intent"] == "Share_Hobby" and intent["confidence"] > 0.6:
                for entity in watson_response["entities"]:
                    if entity["entity"] == "hobby":
                        hobby = Hobby()
                        hobby.created_at = time.time()
                        hobby.user = sender_id
                        hobby.value = entity["value"]
                        hobby.save()

    def save_message(self, facebook_entry, session):
        sender_id = facebook_entry["messaging"][0]["sender"]["id"]
        recipient_id = facebook_entry["messaging"][0]["recipient"]["id"]
        timestamp = round(facebook_entry["messaging"][0]["timestamp"]/1000)
        text = facebook_entry["messaging"][0]["message"]["text"]
        id = facebook_entry["messaging"][0]["message"]["mid"]

        message = Message()
        message.sender_id = sender_id
        message.recipient_id = recipient_id
        message.timestamp = timestamp
        message.text = text
        message.id = id
        message.session = session
        print("555555555")
        print(timestamp)
        message.save()

        return message

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.body.decode('utf-8')
        if (data == None or data == ""):
            return HttpResponse("EVENT_RECIEVED")
        json_data = json.loads(data)
        self.create_message(json_data["entry"][0])
        return HttpResponse("EVENT_RECIEVED")

    def get(self, request, *args, **kwargs):
        print("WHY IS THIS CAlled")
        return HttpResponse(request.GET.get('hub.challenge'))

class DjangoRunsView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, requuest, *args, **kwargs):
        return HttpResponse("App is live.")