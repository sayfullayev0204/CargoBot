from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import index,order_create,my_posts,my_profile,TelegramUserViewSet, RoleViewSet, CountryViewSet, CentersViewSet, CategoryViewSet, OrderViewSet


router = DefaultRouter()
router.register('telegram-users', TelegramUserViewSet)
router.register('roles', RoleViewSet)
router.register('countries', CountryViewSet)
router.register('centers', CentersViewSet)
router.register('categories', CategoryViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', index, name='home'),
    path('create/',order_create, name='create'),
    path('my_posts/', my_posts, name='my_posts'),
    path('my_profile/', my_profile, name='my_profile'),
]
