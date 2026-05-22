import uuid
from django.db import models
from apps.core.models import School
from apps.accounts.models import User


class Exam(models.Model):
    EXAM_TYPES = [('unit_test', 'Unit Test'), ('mid_term', 'Mid-term'), ('final', 'Final'), ('quarterly', 'Quarterly')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=10, blank=True)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2)
    academic_year = models.CharField(max_length=9, default='2025-2026')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.class_name})"


class ExamResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='exam_results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def percentage(self):
        if self.exam.total_marks:
            return round((self.marks_obtained / self.exam.total_marks) * 100, 1)
        return 0

    @property
    def is_pass(self):
        return self.marks_obtained >= self.exam.passing_marks

    class Meta:
        unique_together = ['exam', 'student']


class ExamAttendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='exam_attendance')
    is_present = models.BooleanField(default=True)

    class Meta:
        unique_together = ['exam', 'student']
