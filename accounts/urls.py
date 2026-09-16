from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('user_create/', views.user_create, name='user_create'),
    path('user-documents/<str:doc_type>/<int:apply_pk>', views.get_user_documents, name='get_user_documents'),
    path('user-tests/<int:test_pk>', views.get_student_test, name='get_student_test'),
    path('documents/<int:id>/', views.documents_input, name='documents_load_page'),
    path('documents_view/<int:id>/', views.upload_documents, name='documents_input_view'),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name="password_reset_complete"),
]