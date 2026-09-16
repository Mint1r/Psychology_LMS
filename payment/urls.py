from django.urls import path
from  . import views


urlpatterns = [
    path('payment/webhook/', views.payment_webhook , name='payment_webhook'),
    path('payment/complited/<uuid:payment_id>', views.payment_complited , name='payment_complited'),
    path('purchase/<int:course_id>/', views.purchase, name='purchase'),
    path('purchase/redirect/<int:course_id>/', views.purchase_redirect, name='purchase_redirect'),
]