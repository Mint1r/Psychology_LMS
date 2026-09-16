from django.contrib import admin
from .models import UserProgress,UserModulProgress,UserLessonProgress
# Register your models here.
class UserProgressAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'id','user', 'status','course'
        )
    search_fields = ('user',)

    fieldsets = (
        ('Главное', {'fields': ('user', 'status',"current_class")}),
    )

class UserModuleProgressAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'id','user', 'status','modul'
        )
    search_fields = ('user',)

    fieldsets = (
        ('Главное', {'fields': ('user', 'status')}),
    )

class UserLessonProgressAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'id','user', 'status','lesson'
        )
    search_fields = ('user',)

    fieldsets = (
        ('Главное', {'fields': ('user', 'status',"lesson")}),
    )




admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(UserModulProgress, UserModuleProgressAdmin)
admin.site.register(UserLessonProgress, UserLessonProgressAdmin)