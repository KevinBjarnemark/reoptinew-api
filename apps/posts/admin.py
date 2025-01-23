from django.contrib import admin
from .models import Post, HarmfulTool, HarmfulMaterial, Material, Tool

admin.site.register(Post)
admin.site.register(HarmfulTool)
admin.site.register(HarmfulMaterial)
admin.site.register(Material)
admin.site.register(Tool)
