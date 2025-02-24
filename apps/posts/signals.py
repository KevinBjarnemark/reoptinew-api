from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import HarmfulToolCategory, HarmfulMaterialCategory
from .constants import HARMFUL_TOOL_CATEGORIES, HARMFUL_MATERIAL_CATEGORIES


@receiver(post_migrate)
def populate_harmful_categories(sender, **kwargs):
    """
    Ensures harmful tool & material categories exist after migrations.

    This function is a Django signal that runs after database migrations
    to ensure the required harmful tool and material categories exist.

    The `kwargs` parameter is included to maintain compatibility with
    Django's signal system, even though it is not used explicitly.
    This avoids potential issues if Django adds extra arguments in
    future versions.
    """
    # Prevent warnings about unused `kwargs`
    # pylint: disable=unused-argument
    if sender.name != "apps.posts":  # Ensure it only runs for this app
        return

    with transaction.atomic():
        for tool in HARMFUL_TOOL_CATEGORIES:
            HarmfulToolCategory.objects.get_or_create(category=tool)

        for material in HARMFUL_MATERIAL_CATEGORIES:
            HarmfulMaterialCategory.objects.get_or_create(category=material)
