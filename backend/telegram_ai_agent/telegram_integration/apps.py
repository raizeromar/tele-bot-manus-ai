from django.apps import AppConfig


class TelegramIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_integration'

    def ready(self):
        import telegram_integration.signals  # noqa
