from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webhooks'

    def ready(self):
        import webhooks.signals  # noqa: F401 — register signal handlers
