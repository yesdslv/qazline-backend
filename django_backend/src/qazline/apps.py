from django.apps import AppConfig


class QazlineConfig(AppConfig):
    name = 'qazline'

    def ready(self):
        import django_backend.src.qazline.signals  # noqa
