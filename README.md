# Django-slack

This is a sample application I made for teaching how to integrate [Slack](https://slack.com) with Django.

With these principles, you can :

- Interact with your Django application directly from Slack using a [Slash Command](https://api.slack.com/interactivity/slash-commands).
- Send the content of a form in Slack instead of using Emails using [`Django Forms`](https://docs.djangoproject.com/en/4.1/topics/forms/)
- Send a message in Slack based on [Django Signal](https://docs.djangoproject.com/en/4.1/topics/signals/) in your application (ex: when a new user signs up)
- And many more

All this code comes with unit tests, enjoy!

## django_slack (Django Project)

This is the Django project folder containing the `settings.py` and the main `urls.py`.

### Start the project

Once you created an app and have written your credentials in `.env` you can install the dependencies and run the project mostly like any other Django project.

```sh
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Test the project

You can start the test suite simply by typing `pytest` in a terminal or you can run them directly in VSCode

!(Pytest from VSCode)[screen-pytest.png?raw=true]

### Settings

In `settings.py`, along with the regular Django Settings, I've added

```py
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
```

These variables are found in [Slack API App Dashboard](https://api.slack.com/apps). Instead of editing `settings.py`, I highly recommend to create a file called `.env` at the root of this repository which will be load automatically and, most importantly, ignored by git.

```
# ./env
SLACK_TOKEN=paste_your_slack_token_here
SLACK_SIGNING_SECRET=paste_your_slack_signing_secret_here
```

### DX Extra

I've added a few extra to this project to improve the developer experience. They will be installed with pip.

- [venv](https://docs.python.org/3/library/venv.html) Python's virtual environnement tool to isolate project and dependencies
- [Pylint](https://pypi.org/project/pylint/) A static code analyzer to enforce best practices and python standards
- [autopep8](https://pypi.org/project/autopep8/) A formatter for PEP8 Style Guide for Python Code
- [pytest](https://docs.pytest.org/) Unit test framework that improves on Python's unittest library
- [python-dotenv](https://saurabh-kumar.com/python-dotenv/) Reads from `.env` and sets them as environnement variables
- [isort](https://pycqa.github.io/isort/) isort your imports, so you don't have to.
- `.vscode/settings.json` to integrate all of this with [VSCode](https://code.visualstudio.com/)

I've also added the depencencies and config required for their setup and their integration into VSCode.

## slack_button (Django App)

This is a Django app that uses Django [`Forms`](https://docs.djangoproject.com/en/4.1/topics/forms/) and Django's generic [`FormView`](https://docs.djangoproject.com/en/4.1/ref/class-based-views/generic-editing/#django.views.generic.edit.FormView) to send a message in Slack.

```py
# forms.py

from django import forms
from django.conf import settings
from slack_sdk import WebClient


class SlackButtonForm(forms.Form):
    channel = forms.CharField()
    text = forms.CharField()

    def send_slack_message(self):
        client = WebClient(token=settings.SLACK_TOKEN)
        client.chat_postMessage(channel=self.cleaned_data['channel'], text=self.cleaned_data['text'])
```

```py
# views.py

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from slack_sdk.errors import SlackApiError

from slack_button.forms import SlackButtonForm


class SlackButtonView(FormView):
    template_name = "slack_button/slack_button.html"
    form_class = SlackButtonForm
    success_url = reverse_lazy("slack-button")

    def form_valid(self, form):
        try:
            form.send_slack_message()
            messages.success(self.request, "Message sent successfully")
        except SlackApiError as e:
            messages.error(self.request, e.response["error"])
        return super().form_valid(form)
```

## slack_signals (Django App)

This Django app creates a model so you need to perform the migrations :

```sh
python manage.py migrate
```

Signals are attach to `post_save` and `post_delete` to send a notfication in Slack.

```py
# signals.py
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from slack_sdk import WebClient

from slack_signals.models import Todo

slack_channel = "general"


@receiver(post_save, sender=Todo)
def todo_notify_save(instance, created, **_kwargs):
    action = "Created" if created else "Updated"
    text = f"Todo {action}: {instance}"
    client = WebClient(token=settings.SLACK_TOKEN)
    client.chat_postMessage(channel=slack_channel, text=text)


@receiver(post_delete, sender=Todo)
def todo_notify_delete(instance, **_kwargs):
    text = f"Todo Deleted: {instance}"
    client = WebClient(token=settings.SLACK_TOKEN)
    client.chat_postMessage(channel=slack_channel, text=text)
```

## slack_webhook (Django App)

This app uses a plain [function view](https://docs.djangoproject.com/en/4.1/topics/http/views/) to receive events from Slack API. This is where we'll need the [Slack Signing Secret](https://api.slack.com/authentication/verifying-requests-from-slack). It will verify that the request really comes from Slack.

```py
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from slack_sdk.signature import SignatureVerifier


@require_POST
@csrf_exempt
def webhook_view(request):
    verifier = SignatureVerifier(signing_secret=settings.SLACK_SIGNING_SECRET)
    if not verifier.is_valid_request(request.body.decode("utf-8"), request.headers):
        return HttpResponseForbidden()
    return JsonResponse({"text": "Hello from Django!"})

```

But first we need to setup a [Slash Command](https://api.slack.com/interactivity/slash-commands).

![Setup a Slash Command](screen-slash-command.png?raw=true)

### Request URL

Slack will need a URL to send information to. If you're running the app locally, your laptop is probably not configured to be reachable from the internet. For this, I use popular reverse proxy called [ngrok](https://ngrok.io).

When your app is running locally (by default on port 8000), you can simply open another terminal and type [ngrok http 8000] and it will start a reverse proxy. For example, it will give you something like this

```
Session Status                online
Account                       __@__.com (Plan: Free)
Version                       2.3.40
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://0d33-24-48-109-62.ngrok.io -> http://localhost:8000
Forwarding                    https://0d33-24-48-109-62.ngrok.io -> http://localhost:8000
```

If you click on the https url (ex: https://0d33-24-48-109-62.ngrok.io) you'll be able to access your local application from the internet.

The **Slash Command Request URL**, use this URL but append the path to our webhook (`/slack-webhook/`) which gives somethings like

```
https://xxxx-xx-xx-xxx-xx.ngrok.io/slack-webhook/
```
