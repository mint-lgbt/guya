from django.apps import AppConfig


class MiscConfig(AppConfig):
    name = 'misc'

    def ready(self):
        import misc.signals  # noqa

