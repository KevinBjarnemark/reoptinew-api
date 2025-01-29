from rest_framework import serializers
from static.utils.convert import parse_stringified_object
from .models import (
    HarmfulMaterialCategory,
    HarmfulToolCategory,
    Tool,
    Material,
)


def handle_post_submission(
    post,
    tools_data,
    materials_data,
    harmful_tool_categories_data,
    harmful_material_categories_data,
    clear_existing=False,
):
    """
    Adds or updates related tools, materials, and ManyToMany
    categories.

    :param post: The post instance being created or updated.
    :param tools_data: List of tools to associate with the post.
    :param materials_data: List of materials to associate with the post.
    :param harmful_tool_categories_data: List of tool categories.
    :param harmful_material_categories_data: List of material categories.
    :param clear_existing: If True, clears existing relations (for updates).
    """

    # Clear existing values (most likely updating a post)
    if clear_existing:
        post.tools.all().delete()
        post.materials.all().delete()
        post.harmful_tool_categories.clear()
        post.harmful_material_categories.clear()

    # Add related tools
    for tool in tools_data:
        Tool.objects.create(post=post, **tool)

    # Add related materials
    for material in materials_data:
        Material.objects.create(post=post, **material)

    # Add ManyToMany relationships
    for tool_category in harmful_tool_categories_data:
        tool, _ = HarmfulToolCategory.objects.get_or_create(
            category=tool_category
        )
        post.harmful_tool_categories.add(tool)

    for material_category in harmful_material_categories_data:
        material, _ = HarmfulMaterialCategory.objects.get_or_create(
            category=material_category
        )
        post.harmful_material_categories.add(material)


def validate_harmful_category(value, model, category_name):
    """
    Validator for harmful categories.
    Ensures all provided names exist in the database.
    """
    parsed_value = parse_stringified_object(value)

    # Fetch all valid names from the database
    valid_content = set(
        model.objects.filter(category__in=parsed_value).values_list(
            "category", flat=True
        )
    )
    if isinstance(parsed_value, list) and parsed_value:
        for item in parsed_value:
            if item not in valid_content:
                raise serializers.ValidationError(
                    f"You entered a {category_name} that is not allowed."
                )

    return parsed_value
