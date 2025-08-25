from django.db import models
import uuid


class SurgicalPackage(models.Model):
    medications_included = models.JSONField(default=list, blank=True)
    postoperative_care = models.JSONField(default=list, blank=True)
    hospital_stay_nights = models.IntegerField(default=0)
    special_equipment = models.JSONField(default=list, blank=True)
    dietary_plan = models.BooleanField(default=False)
    additional_services = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"SurgicalPackage {self.id}"


class Quote(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)

    # Patient
    patient_id = models.CharField(max_length=100, null=True, blank=True)
    patient_age = models.IntegerField(null=True, blank=True)
    patient_phone = models.CharField(max_length=50, null=True, blank=True)
    patient_email = models.CharField(max_length=200, null=True, blank=True)

    # Procedure
    procedure_name = models.CharField(max_length=200)
    procedure_code = models.CharField(max_length=100, null=True, blank=True)
    procedure_description = models.TextField(null=True, blank=True)

    # Surgeon
    surgeon_name = models.CharField(max_length=200, null=True, blank=True)
    surgeon_specialty = models.CharField(max_length=200, null=True, blank=True)

    # Surgery details
    surgery_duration_hours = models.IntegerField(default=0)
    anesthesia_type = models.CharField(max_length=200, blank=True)
    additional_equipment = models.JSONField(default=list, blank=True)
    additional_materials = models.JSONField(default=list, blank=True)
    is_ambulatory = models.BooleanField(default=True)
    hospital_nights = models.IntegerField(default=0)

    # Costs
    facility_fee = models.FloatField(default=0.0)
    equipment_costs = models.FloatField(default=0.0)
    anesthesia_fee = models.FloatField(default=0.0)
    other_costs = models.FloatField(default=0.0)
    total_cost = models.FloatField(default=0.0)

    # Package
    surgical_package = models.ForeignKey(SurgicalPackage, null=True, blank=True, on_delete=models.SET_NULL)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=200, default='system')
    status = models.CharField(max_length=50, default='borrador')
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Quote {self.id} - {self.procedure_name}"
