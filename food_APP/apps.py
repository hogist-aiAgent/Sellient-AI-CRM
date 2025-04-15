from django.apps import AppConfig


class FoodAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'food_APP'

    def ready(self):
        import food_APP.signals  # 👈 this connects your signals
