from django.contrib import admin
from .models import Quote, SurgicalPackage

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'procedure_name', 'created_at', 'created_by')


@admin.register(SurgicalPackage)
class SurgicalPackageAdmin(admin.ModelAdmin):
    list_display = ('id',)
