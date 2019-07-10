from django.test import TestCase
import json
from unittest import mock
from types import SimpleNamespace

VERIFY_TKN = "d1d892cade69e4dc000b6db0d55d93ea734587e04b01bd0c7a"

def create_mock_FB_msg(r_id="12344", text="The message contains text"):
    return  {
            "entry": [{
                "messaging" : [
                    { 
                        "sender": "1234",
                        "message" : text
                    }
                ]
            }]
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
class WebhookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.webhook_endpoint = '/webhook_endpoint/' + VERIFY_TKN + "/"

    def test_webhook_rejects_empty_post_requests(self, mock_send_msg):
        request_data = create_mock_FB_msg(text=None)

        response = self.client.post(
            self.webhook_endpoint, 
            data=json.dumps(request_data), 
            content_type="application/json"
            )

        self.assertEqual(response.status_code, 400)
        # mock_send_msg.assert_not_called() # Facebook bot does not get messaged back


    def test_webhook_accepts_non_empty_post(self, mock_send_msg):
        request_data = create_mock_FB_msg(text="This message has a text field")
        # mock_send_msg.assert_not_called()

        response = self.client.post(
            self.webhook_endpoint, 
            data=json.dumps(request_data), 
            content_type="application/json"
            )

        self.assertEqual(response.status_code, 200)
        # mock_send_msg.assert_called_once()
    
    def test_accepts_multiple_messgages(self, _):
        self.fail("finish test")

    def test_finish(self, _):
        self.fail("Finish writing the unit tests after confirming the general idea works with facebook API")