from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.User)
class MyUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_active"
    )
    list_filter = (
        "email",
        "username",
    )
