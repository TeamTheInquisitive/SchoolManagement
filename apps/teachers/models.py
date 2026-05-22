import uuid
from django.db import models
from apps.core.models import School
from apps.accounts.models import User


# Default privilege templates
CLASS_TEACHER_PRIVILEGES = {
    'attendance': ['view', 'mark', 'edit'],
    'assignments': ['view', 'create', 'edit', 'delete', 'grade'],
    'grades': ['view', 'add', 'edit'],
    'examinations': ['view', 'create', 'edit'],
    'timetable': ['view'],
    'student_info': ['view', 'viewDetails', 'editDetails'],
    'messaging': ['sendToStudents', 'sendToParents'],
    'notifications': ['send'],
    'quiz_management': ['view', 'create', 'edit', 'delete', 'viewResults'],
    'reports': ['view', 'generate'],
}

SUBJECT_TEACHER_PRIVILEGES = {
    'attendance': ['view', 'mark'],
    'assignments': ['view', 'create', 'edit', 'delete', 'grade'],
    'grades': ['view', 'add', 'edit'],
    'examinations': ['view', 'create'],
    'timetable': ['view'],
    'student_info': ['view', 'viewDetails'],
    'messaging': ['sendToStudents', 'sendToParents'],
    'notifications': ['send'],
    'quiz_management': ['view', 'create', 'edit', 'delete', 'viewResults'],
    'reports': ['view'],
}


class TeacherProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    employee_id = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    qualification = models.CharField(max_length=255, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    workload_hours = models.IntegerField(default=0)
    department = models.CharField(max_length=100, blank=True)
    employment_type = models.CharField(max_length=20, default='full-time',
        choices=[('full-time', 'Full-time'), ('part-time', 'Part-time'), ('contract', 'Contract')])
    # Medical details
    blood_group = models.CharField(max_length=5, blank=True)
    medical_conditions = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['school', 'employee_id']

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"


class TeacherClassAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='class_assignments')
    class_name = models.CharField(max_length=20)  # e.g., "10"
    section = models.CharField(max_length=10)      # e.g., "A"
    subject = models.CharField(max_length=100)
    is_class_teacher = models.BooleanField(default=False)
    privileges = models.JSONField(default=dict)    # Granular permissions
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['teacher', 'class_name', 'section', 'subject']

    def __str__(self):
        return f"{self.teacher.user.full_name} - Class {self.class_name}-{self.section} ({self.subject})"

    def save(self, *args, **kwargs):
        # Apply default template if privileges empty
        if not self.privileges:
            self.privileges = CLASS_TEACHER_PRIVILEGES if self.is_class_teacher else SUBJECT_TEACHER_PRIVILEGES
        super().save(*args, **kwargs)


class AdhocClass(models.Model):
    """Substitute/extra classes taken by teacher."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='adhoc_classes')
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=10)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    period = models.CharField(max_length=20)
    reason = models.CharField(max_length=255, blank=True)  # e.g., "Substituting for Mr. X"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
