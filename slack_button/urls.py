from django.urls import path

from . import views

urlpatterns = [
    path('', views.SlackButtonView.as_view(), name='slack-button'),
]
