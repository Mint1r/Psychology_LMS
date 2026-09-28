from django.contrib import admin
from .models import CourseAccess


@admin.register(CourseAccess)
class CourseAccessAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "course",
        "status",
        "granted_at",
        "expires_at",
    )

    list_filter = (
        "status",
        "granted_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
        "user__username",
        "course__title",
    )

    readonly_fields = (
        "granted_at",
    )

    ordering = (
        "-granted_at",
    )