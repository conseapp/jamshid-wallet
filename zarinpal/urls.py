from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.PaymentRequestView.as_view(), name='request'),
    path('verify/', views.PaymentVerifyView.as_view(), name='verify')
]
