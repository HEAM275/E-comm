from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.products.views.category import CategoryProductViewSet
from apps.products.views.product import ProductViewSet

# Creamos el router y registramos nuestros viewsets
router = DefaultRouter()

# Registramos los ViewSets con sus respectivos endpoints
router.register(r'categories', CategoryProductViewSet,
                basename='categoryproduct')
router.register(r'products', ProductViewSet, basename='product')

# Las URLs se generan automáticamente
urlpatterns = [
    path('', include(router.urls)),
]
