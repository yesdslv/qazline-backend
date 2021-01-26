from django.apps import AppConfig


class QazlineConfig(AppConfig):
    name = 'qazline'

    def ready(self):
        import qazline.signals  # noqa
