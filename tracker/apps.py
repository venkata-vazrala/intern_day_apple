from django.apps import AppConfig


class TrackerConfig(AppConfig):
    name = 'tracker'
    verbose_name = 'Automation Build & Test Tracker'

    def ready(self):
        # Import signals to wire up model behaviour when app is ready
        from . import signals  # noqa: F401
