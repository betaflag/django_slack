from django.urls import path

from . import views

urlpatterns = [
    path('', views.webhook_view, name='slack-webhook'),
]
