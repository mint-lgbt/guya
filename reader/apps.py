from django.apps import AppConfig


class ReaderConfig(AppConfig):
    name = 'reader'

    def ready(self):
        import reader.signals  # noqa
