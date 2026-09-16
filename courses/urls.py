from django.urls import path
from  . import views

urlpatterns = [
    path('get_lesson_video/<int:lesson_pk>/<int:course_pk>', views.get_lesson_video, name='get_lesson_video'),
    path('get_lesson_materials/<int:lesson_pk>/<int:course_pk>/<int:material_pk>', views.get_lesson_materials, name='get_lesson_materials'),
]