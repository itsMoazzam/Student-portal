from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)  # Use carefully alongside is_staff and is_superuser


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sub_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_staff': True})

    def __str__(self):
        return self.name

    
class Student(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('subadmin', 'Sub-admin'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    approval_requested = models.BooleanField(default=False)
    admission_number = models.CharField(max_length=50, unique=True, blank=True)  # <-- Added default
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)
    class_id = models.ForeignKey('StudentClass', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    degree_completed = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def save(self, *args, **kwargs):
        if not self.admission_number and self.user:
            base = self.user.username.lower()
            existing = Student.objects.filter(admission_number__startswith=base).count() + 1
            self.admission_number = f"{base}-{str(existing).zfill(3)}"
        super().save(*args, **kwargs)
    
    def get_username(self):
        return self.user.username  # or use self.user.get_full_name()

    get_username.short_description = "Username"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"


class ActivityLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    exam_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject} - {self.student.user.username}"
    
# class Student(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     category = models.CharField(max_length=100, blank=True, null=True)
    # rest of fields...

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    github_repo = models.URLField(blank=True, null=True)
    assigned_to = models.ManyToManyField(Student, related_name='tasks')

class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_link = models.URLField()
    review_status = models.CharField(
        max_length=20,
        choices=[('Satisfied', 'Satisfied'), ('Unsatisfied', 'Unsatisfied'), ('Try Again', 'Try Again')],
        default='Try Again'
    )

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StudentClass(models.Model):  # Do NOT use 'Class' as it's a Python keyword
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



                   