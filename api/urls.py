from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import DepositView, PurchaseView, GetUserBalance

urlpatterns = [
    # path('', include(router.urls), name='api'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('purchase/', PurchaseView.as_view(), name='purchase'),
    path('getbalance/', GetUserBalance.as_view(), name='getbalance')
]
