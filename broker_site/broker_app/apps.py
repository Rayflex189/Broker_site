from django.apps import AppConfig

class BrokerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'broker_app'

    def ready(self):
        import broker_app.signals  # Ensures signals are loaded when the app starts
