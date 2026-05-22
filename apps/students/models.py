import uuid
from django.db import models
from apps.core.models import School
from apps.accounts.models import User


class StudentProfile(models.Model):
    class StudentType(models.TextChoices):
        DAY_SCHOLAR = 'day_scholar', 'Day Scholar'
        HOSTLER = 'hostler', 'Hostler'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    admission_number = models.CharField(max_length=20)
    roll_number = models.CharField(max_length=20)
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=10)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    admission_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    # Day Scholar / Hostler
    student_type = models.CharField(max_length=15, choices=StudentType.choices, default=StudentType.DAY_SCHOLAR)
    hostel_name = models.CharField(max_length=100, blank=True)
    hostel_room = models.CharField(max_length=20, blank=True)

    # Mentor
    mentor = models.ForeignKey('teachers.TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='mentees')

    # Medical
    blood_group = models.CharField(max_length=5, blank=True)
    medical_conditions = models.TextField(blank=True, default='None reported')
    allergies = models.TextField(blank=True, default='None reported')
    religion = models.CharField(max_length=50, blank=True)

    # Transport (normalized FK)
    transport_enrolled = models.BooleanField(default=False)
    transport_route = models.ForeignKey('transport.Route', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    bus = models.ForeignKey('transport.Bus', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    pickup_point = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['school', 'admission_number']
        indexes = [
            models.Index(fields=['school', 'class_name', 'section']),
            models.Index(fields=['school', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.full_name} ({self.admission_number})"


class ParentGuardian(models.Model):
    """Normalized parent/guardian - one student can have multiple guardians."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='guardians')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=50, default='Parent')
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    is_emergency_contact = models.BooleanField(default=False)
    occupation = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=True)

    class Meta:
        ordering = ['-is_primary']


class DailyAttendance(models.Model):
    """Daily attendance per student per subject."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='daily_attendance')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    date = models.DateField()
    subject = models.CharField(max_length=100)
    is_present = models.BooleanField(default=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'date', 'subject']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['school', 'date', 'subject']),
        ]
        ordering = ['-date']


class BehaviorRecord(models.Model):
    """Behavior & conduct tracking."""
    RATING_CHOICES = [('A', 'Excellent'), ('B', 'Very Good'), ('C', 'Good'), ('D', 'Needs Improvement'), ('F', 'Poor')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='behavior_records')
    overall_rating = models.CharField(max_length=1, choices=RATING_CHOICES, default='B')
    discipline_score = models.IntegerField(default=90)  # percentage
    punctuality_score = models.IntegerField(default=90)  # percentage
    academic_year = models.CharField(max_length=9, default='2025-2026')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'academic_year']


class ConductNote(models.Model):
    """Individual conduct notes by teachers."""
    SENTIMENT_CHOICES = [('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='conduct_notes')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='given_conduct_notes')
    note = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='positive')
    subject = models.CharField(max_length=100, blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']


class ParentMeeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='parent_meetings')
    date = models.DateField()
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    conducted_by = models.ForeignKey('teachers.TeacherProfile', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']


class StudentActivity(models.Model):
    """Extra-curricular activities, awards."""
    ACTIVITY_TYPES = [('activity', 'Activity'), ('award', 'Award')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=100, blank=True)
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
