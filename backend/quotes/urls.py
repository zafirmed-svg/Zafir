from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuoteViewSet, SurgicalPackageViewSet

# Crea un router y registra nuestros viewsets.
router = DefaultRouter()
router.register(r'quotes', QuoteViewSet, basename='quote')
router.register(r'packages', SurgicalPackageViewSet, basename='surgicalpackage')

# Las URLs de la API son determinadas automáticamente por el router.
urlpatterns = [
    path('', include(router.urls)),
]