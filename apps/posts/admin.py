from django.contrib import admin
from .models import (
    Post,
    HarmfulToolCategory,
    HarmfulMaterialCategory,
    Material,
    Tool,
    Like,
)

admin.site.register(Post)
admin.site.register(HarmfulToolCategory)
admin.site.register(HarmfulMaterialCategory)
admin.site.register(Material)
admin.site.register(Tool)
admin.site.register(Like)
