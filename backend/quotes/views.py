from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Quote, SurgicalPackage
from .serializers import QuoteSerializer, SurgicalPackageSerializer

class QuoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver o editar cotizaciones.
    Proporciona acciones de .list(), .retrieve(), .create(), .update(), .destroy()
    """
    queryset = Quote.objects.all().order_by('-created_at')
    serializer_class = QuoteSerializer

class SurgicalPackageViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver o editar paquetes quirúrgicos.
    """
    queryset = SurgicalPackage.objects.all()
    serializer_class = SurgicalPackageSerializer
