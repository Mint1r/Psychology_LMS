from django.contrib import admin
# не обязательно, но удобно для отладки
from .models import Course,CourseModule,ModuleLesson,Module,Lesson, LessonMaterials

# Register your models here.
class ModuleLessonInline(admin.TabularInline):  
    model = ModuleLesson  
    extra = 1  

class ModuleAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = (
        'title',
        )
    search_fields = ('title',)

    fieldsets = (
        ('Главное', {'fields': ('title',)}),
        ('Отображение на сайте', {'fields': ( 'description',)}),
    )
    inlines = [ModuleLessonInline]

class CourseModuleInline(admin.TabularInline): 
    model = CourseModule  
    extra = 1  

class CourseAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = (
        'title',
        )
    search_fields = ('title',)

    fieldsets = (
        ('Главное', {'fields': ('title','price', 'image')}),
        ('Отображение на сайте', {'fields': ( 'short_description','description','lenth','output',)}),
    )
    inlines = [CourseModuleInline]

class LessonAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = (
        'title',
        )
    search_fields = ('title',)

    fieldsets = (
        ('Главня', {'fields': ('title','text_info','description')}),
        ('Видео и тест', {'fields': ('has_video','video','test')}),
    )
class LessonMaterialsAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_display = (
        'title', 'order'
        )
    search_fields = ('title',)

    fieldsets = (
        ('Главня', {'fields': ('title','order','lesson')}),
        ('Файлы', {'fields': ('material_type','necessity','file', 'link')}),
    )

# Регистрация моделей
# --------------------------
admin.site.register(Course, CourseAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonMaterials, LessonMaterialsAdmin)