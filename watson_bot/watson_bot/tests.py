from django.test import TestCase
import json

class MiscTests(TestCase):
    def test_admin_url_disabled(self):
        response = self.client.get("admin")
        self.assertEqual(404, response.status_code)


class WebhookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.webhook_endpoint = '/webhook_endpoint/'

    def test_webhook_rejects_empty_post_requests(self):
        empty_request_data = json.dumps({"msg": "", "another_field": ''})
        none_request_data = json.dumps({"msg": None})

        response = self.client.post(
            self.webhook_endpoint, 
            data=empty_request_data, content_type="application/json"
            )
        response2 = self.client.post(
            self.webhook_endpoint, 
            data=none_request_data, content_type="application/json"
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response2.status_code, 400)


    def test_webhook_accepts_non_empty_post(self):
        valid_request_data = json.dumps({"msg": "Hi there"})
        response = self.client.post(
            self.webhook_endpoint, 
            data=valid_request_data, content_type="application/json"
            )
        self.assertEqual(response.status_code, 200)
