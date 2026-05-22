import uuid
from django.db import models
from apps.core.models import School
from apps.accounts.models import User


class LeaveType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='leave_types')
    name = models.CharField(max_length=50)  # Casual, Sick, Earned, etc.
    max_days = models.IntegerField(default=12)
    applicable_to = models.CharField(max_length=20, choices=[('teacher', 'Teacher'), ('student', 'Student'), ('both', 'Both')])

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)  # e.g., "2025-2026"
    total = models.IntegerField(default=0)
    used = models.IntegerField(default=0)

    @property
    def pending(self):
        return LeaveApplication.objects.filter(user=self.user, leave_type=self.leave_type, status='pending').count()

    @property
    def remaining(self):
        return self.total - self.used

    class Meta:
        unique_together = ['user', 'leave_type', 'academic_year']


class LeaveApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_applications')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    class Meta:
        ordering = ['-created_at']
