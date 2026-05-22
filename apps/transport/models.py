import uuid
from django.db import models
from apps.core.models import School
from apps.accounts.models import User


class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=100)
    stops = models.JSONField(default=list)  # List of stop names
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Bus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='buses')
    number = models.CharField(max_length=20)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, related_name='buses')
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    capacity = models.IntegerField(default=40)
    is_active = models.BooleanField(default=True)


class StaffProfile(models.Model):
    STAFF_TYPES = [('non_teaching', 'Non-Teaching'), ('admin_staff', 'Admin Staff'), ('support', 'Support')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='staff_members')
    employee_id = models.CharField(max_length=20)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['school', 'employee_id']


class SalaryStructure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary_structure')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def net_salary(self):
        return self.basic_salary + self.hra + self.allowances - self.deductions


class Payslip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payslips')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'month', 'year']
        ordering = ['-year', '-month']
