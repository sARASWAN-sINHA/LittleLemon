from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CartViewSet, 
                    ManagerViewSet, 
                    DeliveryCrewViewSet, 
                    MenuItemViewSet, 
                    CustomerView, 
                    OrderViewSet, 
                    CategoryViewSet, 
                    SetFeaturedView)


router = DefaultRouter(trailing_slash = False)
router.register('menu-items', viewset= MenuItemViewSet, basename='menuitems-view')
router.register('groups/managers/users', viewset=ManagerViewSet, basename='manager-view')
router.register('groups/delivery-crew/users', viewset=DeliveryCrewViewSet, basename='delivery-crew-view')
router.register('cart/menu-items', viewset=CartViewSet, basename='cart-view')
router.register('orders', viewset=OrderViewSet, basename='order-view')
router.register('category', viewset=CategoryViewSet, basename='category-view')

urlpatterns = [
    path('', include(router.urls)),
    path('groups/customer/users', CustomerView.as_view()),
    path('set-featured/<int:pk>', SetFeaturedView.as_view()),
    path('', include('djoser.urls')),
]