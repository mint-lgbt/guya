from django.apps import AppConfig


class ReaderConfig(AppConfig):
    name = 'reader'
    verbose_name = _("reader")

    def ready(self):
        import reader.signals  # noqa
