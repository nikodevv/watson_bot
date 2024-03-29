import json, requests, time
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.db.utils import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from watson_bot.models import Session, Message, Hobby
from watson_bot.utilities.watson_interface import WatsonInterface
from watson_bot.serializers import MessageSerializer, HobbySerializer

watson = WatsonInterface() # Makes calls to watson API
SESSION_TIMEOUT = 5*60 - 10 # Session timeout after this long
WATSON_FB_ID = 437600817089858 # the user id of the facebook page
FB_VERIFY_TKN = "d1d892cade69e4dc000b6db0d55d93ea734587e04b01bd0c7a"
FB_PAGE_ACCESS_TOKEN = (
    "EAAGGuYZBs8B4BACPVaQaJu1tQYjZC2hTDW2PnIlNilB9HGrh87ZBXzbGdUpjK1muwoILz"
    + "VuPZBT8uZABxXbWMVkMWrifmoITLxd8AXTGhD2PHzZCAwmUpLBN9lGt1lYp3otXl27u0"
    + "l5TzCUf5Jh1bbhZCMWKrpJUcArJyPMtdqipAZDZD")

def send_message(recipient_id, message):
    """
    Sends a message to a facebook user
    """
    endpoint = f"https://graph.facebook.com/v2.6/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    payload = json.dumps({
            "messaging_type": "RESPONSE",
            "recipient": { "id": recipient_id },
            "message": { "text": message } 
            })
    status = requests.post(
        endpoint, 
        headers={"Content-Type": "application/json"},
        data=payload)
    return status.json()

class FacebookWebhookView(View):

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
        return HttpResponse(request.GET.get('hub.challenge'))

    # Utility methods #
    def save_session(self, session_id):
        """
        Instanties a Session model and saves it to database
        """
        timestamp = time.time()

        session = Session()
        session.session_id = session_id
        session.created_at = timestamp
        session.last_renewed = timestamp
        session.save()
        return session

    def renew_session(self, session_id):
        """
        Renews session metadata in the database.
        """
        timestamp = time.time()
        session = Session.objects.get(pk=session_id)
        session.last_renewed = timestamp
        session.save()

    def should_renew_session(self, session):
        """
        Returns true if the session can be renewed.
        """
        return session.last_renewed + SESSION_TIMEOUT > time.time()


    def should_create_message(self, facebook_entry):
        """
        Returns true if the the sender of the facebook message JSON is not the watson bot.
        """
        for indx, obj in enumerate(facebook_entry["messaging"]):
            if "sender" in obj and obj["sender"] == WATSON_FB_ID:
                # if the sender is the bot messages are saved when they are sent
                # not received
                return False
        return True

    def get_sender_id(self, facebook_entry):
        """
        Returns the sender id from a facebook message JSON
        """
        for obj in facebook_entry["messaging"]:
            if "sender" in obj:
                return obj["sender"]["id"]

    def create_message(self, facebook_entry):
        """
        Calls build steps for saving a facebook message.
        """
        min_timestamp_before_timeout = time.time() - SESSION_TIMEOUT
        sender_id = self.get_sender_id(facebook_entry)

        recent_msgs = Message.objects.filter(
            timestamp__gt=min_timestamp_before_timeout,
            sender_id__exact=sender_id)

        if (len(recent_msgs) == 0):
            session_id = watson.create_session()["session_id"]
            session = self.save_session(session_id)

        elif (self.should_renew_session(recent_msgs[0].session) == False):
            # Create new session
            session_id = watson.create_session()["session_id"]
            session = self.save_session(session_id)
        
        else: 
            session = recent_msgs[0].session
            self.renew_session(session.session_id)


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
                        try: 
                            hobby.save()
                        except IntegrityError:
                            # Duplicate user-hobby entries are not logged.
                            pass

    def save_message(self, facebook_entry, session):
        """
        Instantiates a message model and saves it to database.
        """
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
        message.save()

        return message

class MessageView(View):
    """
    API view for messages
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, requuest, *args, **kwargs):
        msgs = Message.objects.all()
        serializer = MessageSerializer(msgs, many=True)
        return JsonResponse(serializer.data, safe=False)

class HobbyView(View):
    """
    API view for hobbies
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, requuest, *args, **kwargs):
        hobbies = Hobby.objects.all()
        serializer = HobbySerializer(hobbies, many=True)
        return JsonResponse(serializer.data, safe=False)

# Homepage
class DjangoRunsView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, requuest, *args, **kwargs):
        return HttpResponse("App is live.")