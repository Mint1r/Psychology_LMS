from django.contrib import admin
from .models import User,UserDocuments,UserTests
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_per_page = 15
    list_display = (
        'username',
        )
    search_fields = ('username',)

    fieldsets = (
        ('Главное', {'fields': ('username','phone_number','email')}),
        ('Права доступа', {
            'fields': (
                'is_active',
                'is_staff', 
                'is_superuser',
                'groups',  
                'user_permissions',
            ),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

class UserDocumentsAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'id','user', 'status'
        )
    search_fields = ('user',)

    fieldsets = (
        ('Главное', {'fields': ('user', 'status')}),
    )

class UserTestsAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = (
        'user', 'status'
        )
    search_fields = ('user',)

    fieldsets = (
        ('Главное', {'fields': ('user', 'status','test_results')}),
    )

admin.site.register(UserTests, UserTestsAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserDocuments, UserDocumentsAdmin)

