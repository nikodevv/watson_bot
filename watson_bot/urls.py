"""watson_bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path
from .views import FacebookWebhookVew, DjangoRunsView

VERIFY_TKN = "d1d892cade69e4dc000b6db0d55d93ea734587e04b01bd0c7a"

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path(r'webhook', FacebookWebhookVew.as_view(), name="webhook"),
    re_path('', DjangoRunsView.as_view(), name="homepage"),
]
