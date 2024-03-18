from django.apps import AppConfig


class RankingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rankings'

    def ready(self):
        import rankings.signals
