from django.contrib import admin
from .models import Post, HarmfulTool, HarmfulMaterial

admin.site.register(Post)
admin.site.register(HarmfulTool)
admin.site.register(HarmfulMaterial)
