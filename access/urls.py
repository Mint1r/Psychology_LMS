from django.urls import path
from  . import views

app_name='learn'

urlpatterns = [
    path('', views.learn_main, name='learn_main'),
    path('course/<int:course_id>', views.learn_course, name='learn_course'),
    path('lesson/<int:course_id>/<int:lesson_id>', views.learn_lesson, name='learn_lesson'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('applications/decision/', views.applications, name='applications'),
    path('tests/decision/', views.test_decision, name='test_cheek'),
    path('lesson/complite/<int:course_id>/<int:lesson_id>', views.complit_lesson, name='complit_lesson'),
    path('lesson/load_test/<int:course_id>/<int:lesson_id>', views.load_test, name='load_test'),
]