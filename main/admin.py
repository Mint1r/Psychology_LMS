from django.contrib import admin
from .models import Documents

# Register your models here.
class DocumentsAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = (
        'id', 'title'
        )
    search_fields = ('title',)

    fieldsets = (
        ('Главное', {'fields': ('title', 'link')}),
    )

admin.site.register(Documents, DocumentsAdmin)