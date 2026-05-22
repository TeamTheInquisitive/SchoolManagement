import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import School
from apps.accounts.models import User


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=100, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BookIssue(models.Model):
    class Status(models.TextChoices):
        ISSUED = 'issued', 'Issued'
        RETURNED = 'returned', 'Returned'
        OVERDUE = 'overdue', 'Overdue'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_issues')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_days = models.IntegerField(default=14)  # Number of days allowed
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ISSUED)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timezone.timedelta(days=self.due_days)
        super().save(*args, **kwargs)

    @property
    def overdue_days(self):
        if self.status == 'issued' and timezone.now().date() > self.due_date:
            return (timezone.now().date() - self.due_date).days
        return 0

    def calculate_fine(self, fine_per_day=2):
        """Calculate fine based on overdue days."""
        if self.overdue_days > 0:
            self.fine_amount = self.overdue_days * fine_per_day
            self.status = 'overdue'
            self.save()
        return self.fine_amount

    class Meta:
        ordering = ['-issue_date']


class LibrarySettings(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='library_settings')
    default_issue_days = models.IntegerField(default=14)
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    max_books_per_student = models.IntegerField(default=3)
