from django.test import TestCase
import json
from unittest import mock
import time
from django.test.client import RequestFactory
from .views import FacebookWebhookView
from watson_bot.env import FB_VERIFY_TKN, WATSON_FB_ID
from watson_bot.models import Message, Session

def create_mock_FB_msg(json_string=True):
    msg = {
        "object" : "page",
        "entry": [
            {
                "id" : "3",
                "messaging" : [
                    { 
                        "sender" : { "id" : "SENDER_UNIQUE_ID"} ,
                        "recipient" : { "id" : "UNIQUE_RECIPIENT_ID"},
                        "timestamp": time.time(),
                        "mid": "UNIQUE_MSG_ID",
                        "message" : {
                            "mid" : "UNIQUE_MESSAAGE_ID",
                            "text": "Some sser text message lmfao"
                        }
                    }
                ]
            }
        ]
    }
    if json_string == False:
        return msg
    return json.dumps(msg)

class MiscTests(TestCase):
    def test_admin_url_disabled(self):
        response = self.client.get("admin")
        self.assertEqual(404, response.status_code)

    def test_homepage(self):
        response = self.client.get("")
        self.assertEqual(200, response.status_code)

# Facebook requests are mocked
@mock.patch('watson_bot.views.send_message', side_effect=None)
@mock.patch('watson_bot.views.FacebookWebhookView.create_watson_session', side_effect=None)
@mock.patch('watson_bot.views.FacebookWebhookView.create_session', return_value="uniqueSessionId", side_effect=None)
@mock.patch('watson_bot.views.FacebookWebhookView.log', side_effect=None)
class WebhookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.webhook_endpoint = '/webhook?hub.verify_token=' + FB_VERIFY_TKN

    def test_post_requests_are_logged(self, mock_log, *args):
        mock_log.assert_not_called()
        request_data = create_mock_FB_msg()
        rf = RequestFactory()

        request = rf.post(self.webhook_endpoint, 
            data = request_data, content_type="application/json")
        view = FacebookWebhookView()

        view.post(request)
        mock_log.assert_called_once()
        mock_log.assert_called_with(request)


    def test_post_returns_200_with_valid_token(self, *args):
        response = self.client.post(self.webhook_endpoint, 
            create_mock_FB_msg(), content_type="application/json")
        # URL set up in setUp method has to have a valid token as query param to pass
        self.assertEqual(response.status_code, 200)

    def test_post_returns_200_with_invalid_token(self, *args):
        URL_WITH_INVALID_QUERY_PARAM  = self.webhook_endpoint[0:-3]
        response = self.client.post(URL_WITH_INVALID_QUERY_PARAM, 
            create_mock_FB_msg(), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_returns_challenge_token_on_get_request(self, mock_log, *args):
        url = self.webhook_endpoint
        token = "myCustomAndUniqueToken"
        query = "&hub.challenge=" + token
        response = self.client.get(url + query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), token)

    def test_saves_session(self, *args):
        sessions = Session.objects.all()
        self.assertEqual(len(sessions), 0)
        id = '3333123098'
        FacebookWebhookView().save_session(id)
        sessions = Session.objects.all()
        self.assertEqual(len(sessions), 1)
        # The item was logged as being created within 1 second ago
        timestamp = time.time()
        self.assertTrue(sessions[0].created_at - 1 < timestamp)
        self.assertTrue(sessions[0].last_renewed - 1 < timestamp)
        self.assertEqual(sessions[0].session_id, id)


    def test_save_session_returns_session(self, *args):
        sessions = Session.objects.all()
        self.assertEqual(len(sessions), 0)
        id = 3333123098
        session = FacebookWebhookView().save_session(id)
        self.assertIsInstance(session, Session)

    def test_should_create_session_called_if_no_valid_session_exists(self, *args):
        self.assertEqual(len(Session.objects.all()),0)
        timestamp = time.time() - 350 # 5 minutes ago, aka max session exipres
        session = Session()
        session.created_at = timestamp
        session.last_renewed = timestamp
        session.id = "123"
        session.save()
        self.fail("Finish test")

    def test_should_renew_session_returns_true_if_max_time_elapsed(self, *args):
        view = FacebookWebhookView()
        expired_timestamp = time.time() - 350 # 5 minutes ago, aka max session exipres
        id = "123507509"
        session = Session()
        session.created_at = expired_timestamp
        session.last_renewed = expired_timestamp
        session.id = id

        self.assertTrue(view.should_renew_session(session))
        session.last_renewed = time.time()
        self.assertFalse(view.should_renew_session(session))

    def test_should_create_message_returns_true_if_sender_is_not_waston(self, *args):
        msg = create_mock_FB_msg(json_string=False)
        entry = msg["entry"][0]
        view = FacebookWebhookView()
        self.assertTrue(view.should_create_message(entry))

        for indx, obj in enumerate(entry["messaging"]):
            if "sender" in obj:
                entry["messaging"][indx]["sender"] = WATSON_FB_ID
        self.assertFalse(view.should_create_message(entry))

    def test_renews_session(self, *args):
        id = "1233415409818931"
        session = Session()
        session.session_id = id
        session.last_renewed = 1
        session.created_at = 1
        session.save()

        session = Session.objects.get(session_id=id)
        self.assertFalse(session.last_renewed + 1 > time.time())
        self.assertTrue(session.last_renewed < time.time())
        FacebookWebhookView().renew_session(id)
        session = Session.objects.get(session_id=id)
        self.assertTrue(session.last_renewed + 1 > time.time())
        self.assertTrue(session.last_renewed < time.time())


    def test_get_sender_id_returns_sender_id(self, *args):
        view = FacebookWebhookView()
        msg = create_mock_FB_msg(json_string=False)
        # Should match default sender id as defined in FB msg builder
        self.assertEqual( view.get_sender_id(msg["entry"][0]), "SENDER_UNIQUE_ID")

    def test_saves_messages(self, *args):
        session = Session()
        session.session_id = "RANDOM_SESSION_ID"
        session.last_renewed = 1
        session.created_at = 1
        session.save()
        view = FacebookWebhookView()
        facebook_msg = create_mock_FB_msg(json_string=False)["entry"][0]

        self.assertEqual(len(Message.objects.all()), 0)

        view.save_message(facebook_msg, session)
        messages = Message.objects.all()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].session, session)
        self.assertEqual(messages[0].id, facebook_msg["messaging"][0]["message"]["mid"])
        self.assertEqual(messages[0].text, facebook_msg["messaging"][0]["message"]["text"])
        self.assertEqual(messages[0].sender_id, facebook_msg["messaging"][0]["sender"]["id"])
        self.assertEqual(messages[0].recipient_id, facebook_msg["messaging"][0]["recipient"]["id"])
        
    def test_save_message_retusn_message(self, *args):
        session = Session()
        session.session_id = "RANDOM_SESSION_ID"
        session.last_renewed = 1
        session.created_at = 1
        session.save()
        view = FacebookWebhookView()
        facebook_msg = create_mock_FB_msg(json_string=False)["entry"][0]

        self.assertIsInstance(view.save_message(facebook_msg, session), Message)
        

    def test_accepts_multiple_messgages(self, *args):
        self.fail("finish test")