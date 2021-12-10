from django.contrib import admin

from . import models


@admin.register(models.User)
class MyUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_active",
        "id"
    )
    list_filter = (
        "email",
        "username",
    )
    search_fields = (
        "username",
    )
