from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import PurchaseView, GetUserBalance, CancelEvent

urlpatterns = [

    path('purchase/', PurchaseView.as_view(), name='purchase'),
    path('getbalance/', GetUserBalance.as_view(), name='getbalance'),
    path('cancel/', CancelEvent.as_view(), name='cancel')
]
