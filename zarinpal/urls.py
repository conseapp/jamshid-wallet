# Github.com/Rasooll
from django.urls import path
from . import views
from . import views2

urlpatterns = [
    path('request/', views.send_request, name='request'),
    path('verify/', views.verify, name='verify'),
    path('req/', views2.PaymentRequestView.as_view(), name='req'),
    path('ver/', views2.PaymentVerifyView.as_view(), name='ver')
]
