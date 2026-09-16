from django.contrib import admin
from .models import UserPayments

@admin.register(UserPayments)
class UserPaymentsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'course',
        'amount',
        'status',
        'provider_payment_id',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'created_at',
        'course',
    )

    search_fields = (
        'user__username',
        'user__email',
        'provider_payment_id',
        'course__title',
    )

    readonly_fields = (
        'user',
        'course',
        'amount',
        'status',
        'provider_payment_id',
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)

