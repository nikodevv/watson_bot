from django.test import TestCase
import json
from unittest import mock
from django.test.client import RequestFactory
from .views import FacebookWebhookVew

VERIFY_TKN = "d1d892cade69e4dc000b6db0d55d93ea734587e04b01bd0c7a"

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
@mock.patch('watson_bot.views.FacebookWebhookVew.log', side_effect=None)
class WebhookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.webhook_endpoint = '/webhook?hub.verify_token=' + VERIFY_TKN

    def test_post_requests_are_logged(self, mock_log, _):
        mock_log.assert_not_called()
        request_data = create_mock_FB_msg()
        rf = RequestFactory()

        request = rf.post(self.webhook_endpoint, 
            data = request_data, content_type="application/json")
        view = FacebookWebhookVew()

        view.post(request)
        mock_log.assert_called_once()
        mock_log.assert_called_with(request)


    def test_post_returns_200_with_valid_token(self, _, _2):
        # URL set up in setUp has valid token as query param
        response = self.client.post(self.webhook_endpoint, 
            create_mock_FB_msg(), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_post_returns_200_with_invalid_token(self, _, _2):
        URL_WITH_INVALID_QUERY_PARAM  = self.webhook_endpoint[0:-3]
        response = self.client.post(URL_WITH_INVALID_QUERY_PARAM, 
            create_mock_FB_msg(), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_returns_challenge_token_on_get_request(self, mock_log, _):
        url = self.webhook_endpoint
        token = "myCustomAndUniqueToken"
        query = "&hub.challenge=" + token
        response = self.client.get(url + query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), token)

    def test_accepts_multiple_messgages(self, _, _2):
        self.fail("finish test")