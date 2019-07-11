from django.test import TestCase
import json
from unittest import mock
import time
from django.test.client import RequestFactory
from .views import FacebookWebhookView
from watson_bot.env import FB_VERIFY_TKN
from watson_bot.models import Message, Session

def create_mock_FB_msg():
    return  json.dumps({
        "object" : "page",
        "entry": [
            {
                "id" : "3"
            }
        ]
    })

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
        # URL set up in setUp has valid token as query param
        response = self.client.post(self.webhook_endpoint, 
            create_mock_FB_msg(), content_type="application/json")
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
        """
        A message is valid if it contains the correct verification token, and
        has a payload in the expected format.
        """
        sessions = Session.objects.all()
        self.assertEqual(len(sessions), 0)
        id = 3333123098
        FacebookWebhookView.save_session(id)
        sessions = Session.objects.all()
        self.assertEqual(len(sessions), 1)
        # The item was logged as being created within 1 second ago
        timestamp = time.time()
        self.assertTrue(sessions[0].created_at - 1 < timestamp)
        self.assertTrue(sessions[0].last_updated - 1 < timestamp)
        self.assertEqual(sessions[0].id, id)

    def test_should_create_session_called_if_no_valid_session_exists(self, *args):
        self.fail("Finish test")


    def test_accepts_multiple_messgages(self, *args):
        self.fail("finish test")