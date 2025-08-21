from rest_framework import serializers
from .models import Quote, SurgicalPackage

class SurgicalPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurgicalPackage
        fields = ['id', 'package_name', 'suggested_price', 'final_price']


class QuoteSerializer(serializers.ModelSerializer):
    #Esto anida los paquetes quirúrgicos dentro de la respuesta de la cotización
    surgical_packages = SurgicalPackageSerializer(many=True, read_only=True )

    class Meta:
        model = Quote
        #Campos que se incluiran en la API para la cotizacion

        fields = [
            'id',
            'quote_id',
            'patient_name',
            'created_at',
            'date_of_birth',
            'procedure_date',
            'hospital',
            'doctor',
            'total_suggested_price',
            'total_final_price',
            'status',
            'surgical_packages' # incluimos la lista de paquetes anidados
        ]