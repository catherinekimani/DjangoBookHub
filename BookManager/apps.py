from django.apps import AppConfig


class BookmanagerConfig(AppConfig):
    """Configuration for BookManager app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BookManager'

    def ready(self):
        """Import signals when app is ready."""
        import BookManager.signals