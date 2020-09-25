from django.apps import AppConfig


class MiscConfig(AppConfig):
    name = 'misc'
    verbose_name = _("misc")

    def ready(self):
        import misc.signals  # noqa

