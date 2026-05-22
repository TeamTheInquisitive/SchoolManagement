import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import School
from apps.accounts.models import User


class FeeType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_types')
    name = models.CharField(max_length=100)  # Tuition, Transport, Hostel, Lab, Library
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('annually', 'Annually'), ('one_time', 'One Time')
    ])
    applicable_to = models.CharField(max_length=20, choices=[
        ('all', 'All'), ('day_scholar', 'Day Scholar'), ('hostler', 'Hostler')
    ], default='all')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class FeeAssignment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PARTIAL = 'partial', 'Partial'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='fee_assignments')
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    academic_year = models.CharField(max_length=9, default='2025-2026')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def balance(self):
        return self.total_amount + self.fine_amount - self.paid_amount

    @property
    def is_overdue(self):
        return self.status != 'paid' and timezone.now().date() > self.due_date

    class Meta:
        ordering = ['-due_date']


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fee_assignment = models.ForeignKey(FeeAssignment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'), ('cheque', 'Cheque'), ('upi', 'UPI'), ('bank_transfer', 'Bank Transfer')
    ])
    receipt_number = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class LateFineRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fine_rules')
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, null=True, blank=True)
    fine_type = models.CharField(max_length=20, choices=[
        ('fixed_per_day', 'Fixed Per Day'), ('percentage', 'Percentage'), ('slab', 'Slab Based')
    ])
    amount = models.DecimalField(max_digits=8, decimal_places=2)  # per day or percentage
    grace_period_days = models.IntegerField(default=7)
    max_fine_cap = models.DecimalField(max_digits=8, decimal_places=2, default=500)


class FeeReminder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    target_group = models.CharField(max_length=50)  # "class:10", "section:10-A", "all", "overdue"
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients_count = models.IntegerField(default=0)
