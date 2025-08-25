from rest_framework import serializers
from .models import Quote, SurgicalPackage


class SurgicalPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurgicalPackage
        fields = '__all__'


class QuoteSerializer(serializers.ModelSerializer):
    surgical_package = SurgicalPackageSerializer(required=False, allow_null=True)

    class Meta:
        model = Quote
        fields = '__all__'

    def create(self, validated_data):
        package_data = validated_data.pop('surgical_package', None)
        package = None
        if package_data:
            package = SurgicalPackage.objects.create(**package_data)
        quote = Quote.objects.create(surgical_package=package, **validated_data)
        return quote

    def update(self, instance, validated_data):
        package_data = validated_data.pop('surgical_package', None)
        if package_data:
            if instance.surgical_package:
                for k, v in package_data.items():
                    setattr(instance.surgical_package, k, v)
                instance.surgical_package.save()
            else:
                instance.surgical_package = SurgicalPackage.objects.create(**package_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
