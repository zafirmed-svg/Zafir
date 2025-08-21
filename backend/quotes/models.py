from django.db import models
from django.utils import timezone

class Quote(models.Model):
    """
    Representa una cotización completa.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]

    quote_id = models.CharField(max_length=50, unique=True, help_text="ID legible para la cotización, ej: Q-2025-001")
    patient_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    date_of_birth = models.DateField()
    procedure_date = models.DateField()
    hospital = models.CharField(max_length=255)
    doctor = models.CharField(max_length=255)
    total_suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Cotización {self.quote_id} para {self.patient_name}"

class SurgicalPackage(models.Model):
    """
    Representa un paquete o concepto dentro de una cotización.
    Está vinculado a una cotización específica.
    """
    quote = models.ForeignKey(Quote, related_name='surgical_packages', on_delete=models.CASCADE)
    package_name = models.CharField(max_length=255)
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.package_name} (Cotización: {self.quote.quote_id})"
