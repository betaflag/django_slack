from django.apps import AppConfig


class SlackSignalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'slack_signals'

    def ready(self):
        from slack_signals import signals  # pylint: disable=unused-import,import-outside-toplevel
