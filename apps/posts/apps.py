from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.posts"

    def ready(self):
        """
        Import signals to ensure they are registered when the app starts.

        Although this import appears unused, it is necessary to trigger
        Django’s signal detection mechanism. This ensures that post-migration
        actions (such as populating required database categories) execute
        correctly.
        """
        # Supress unused import warnings
        # pylint: disable=unused-import,import-outside-toplevel
        import apps.posts.signals  # noqa: F401
