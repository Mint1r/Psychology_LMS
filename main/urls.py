from django.urls import path
from  . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('catalog/', views.catlog, name='catalog'),
    path('course/<int:course_id>/', views.course, name='course'),
    path('info/', views.info, name='info'),
    path('documents/', views.documents, name='documents_official'),
    path('policy/', views.policy, name='policy'),
    path('documencal_aplyts_view/', views.cal_aply , name='cal_aply'),
]