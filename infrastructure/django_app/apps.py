from django.apps import AppConfig


class LifeAdminConfig(AppConfig):
    name = "infrastructure.django_app"
    label = "life_admin"
    verbose_name = "Life Admin"

    def ready(self) -> None:
        # Import models to ensure they're registered with Django ORM.
        import infrastructure.django_app.models  # noqa: F401
