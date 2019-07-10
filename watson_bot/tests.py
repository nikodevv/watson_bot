from django.test import TestCase
import json
from unittest import mock
from types import SimpleNamespace
from django.test.client import RequestFactory

VERIFY_TKN = "d1d892cade69e4dc000b6db0d55d93ea734587e04b01bd0c7a"

def create_mock_FB_msg():
    return  {
        "object" : "page",
        "entry": [
            {
                "id" : "3"
            }
        ]
    }

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
        cls.webhook_endpoint = 'webhook_endpoint?hub.verify_token=' + VERIFY_TKN

    def test_post_requests_are_logged(self, mock_log, _):
        request_data = create_mock_FB_msg()
        mock_log.assert_not_called()

        rf = RequestFactory() 
        # request = rf.post(self.webhook_endpoint, request_data)
        request = self.client.post(self.webhook_endpoint, data=request_data)
        mock_log.assert_called_with(request, request_data)
    
    def test_accepts_multiple_messgages(self, _):
        self.fail("finish test")