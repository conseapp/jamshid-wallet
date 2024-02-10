from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import ProductViewSet
#
# router = DefaultRouter()
# router.register(r'products', ProductViewSet, basename='product')
# router.register(r'categories', views.CategoryViewSet, basename='category')
# router.register(r'comments', views.CommentViewSet, basename='comment')
# router.register(r'stocks', views.StockViewSet, basename='stock')
# router.register(r'tags', views.TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls), name='api')
]
