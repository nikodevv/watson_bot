import requests, json

# Constants
WATSON_USERNAME = "apikey"
WATSON_PASSWORD = "HICbiU3ag0ViUjg3DlZBcHnOVHj5uJYDTwV-CIAB1x7H"
WATSON_API_VER = "version=2019-02-28"
WATSON_ENDPOINT = ("https://gateway.watsonplatform.net/assistant/api/v2/" 
    + "assistants/11c98e51-0aab-4455-a0bd-b64ffe723145/sessions")

class WatsonInterface:
    """
    Interface for interacting with watson assistant API.
    """
    
    def send_message(self, message_txt, session_id):
        """
        Sends a message to Watson and returns Watson's response in a DICT.
        """
        session = requests.Session()
        session.auth = (WATSON_USERNAME, WATSON_PASSWORD)
        data = { "input" : {"text" : message_txt} }
        response = session.post(
            f'{WATSON_ENDPOINT}/{session_id}/message?{WATSON_API_VER}', 
            json=data)
        return json.loads(response.content.decode("utf-8"))["output"]


    def create_session(self):
        """
        Returns DICT containing newly created session info.
        """
        session = requests.Session()
        session.auth = (WATSON_USERNAME, WATSON_PASSWORD)
        response = session.post(f'{WATSON_ENDPOINT}?{WATSON_API_VER}')
        return json.loads(response.content.decode("utf-8"))
