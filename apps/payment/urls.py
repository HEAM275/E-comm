# apps/payment/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.payment.views.purchase import PurchaseView
from apps.payment.views.order import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order',
                )

urlpatterns = [
    path('purchase/', PurchaseView.as_view(), name='purchase'),
    path('', include(router.urls)),
]
