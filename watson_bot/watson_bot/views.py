import json
import requests, random, re
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def send_message():
    pass

class FacebookWebookVew(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        msg = data['msg']
        if msg == None or msg == "":
            return HttpResponseBadRequest()
        send_message()
        return HttpResponse("Success")