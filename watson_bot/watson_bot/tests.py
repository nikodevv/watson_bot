from django.test import TestCase

class WebhookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def test_test_can_fail(self):
        self.fail("The test fails and hence folder structure is correct")

