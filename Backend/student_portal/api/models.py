from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.utils import timezone


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_subadmin  = models.BooleanField(default=False) 
    is_admin = models.BooleanField(default=False)  # Use carefully alongside is_staff and is_superuser
    # make username optional **at the DB level**
    username    = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text="Optional. Will be auto-generated from first name if omitted."
    )

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']   # full name is now mandatory
    USERNAME_FIELD  = 'username'  # we still authenticate by username (auto-generated if absent)

    def save(self, *args, **kwargs):
        """
        Auto-generate a unique username iff the caller left it blank.
        Uses slugified first part of first_name, then adds a numeric suffix
        if collision occurs.
        """
        if not self.username:
            base = slugify(self.first_name.split()[0]) or "user"
            suffix = 1
            candidate = base
            while User.objects.filter(username=candidate).exists():
                suffix += 1
                candidate = f"{base}{suffix}"
            self.username = candidate
        super().save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


 
class Student(models.Model):
    
    
    user        = models.OneToOneField(User, on_delete=models.CASCADE,limit_choices_to={'is_student': True})
    github_url  = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    approval_requested = models.BooleanField(default=False)
    admission_number = models.CharField(max_length=50, unique=True, blank=True, db_index=True )  # <-- Added default
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)
    class_id = models.ForeignKey('StudentClass', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    degree_completed = models.BooleanField(default=False)
    

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
    

class SubAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='leaders')   # <-- now many-to-many

    def __str__(self):
        cats = ", ".join(self.categories.values_list('name', flat=True)[:3])
        return f"{self.user.username} — {cats}"
    

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
    
# NEW — optional “Team” if you need granularity below Category
class Team(models.Model):
    name        = models.CharField(max_length=100)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    leaders     = models.ManyToManyField(SubAdmin, related_name='teams')
    members     = models.ManyToManyField('Student', related_name='teams')
    created_at  = models.DateTimeField(auto_now_add=True)


# CHANGED — Task can target students OR teams/categories; track author & status
class Task(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    title        = models.CharField(max_length=255)
    description  = models.TextField()
    deadline     = models.DateTimeField()                        # <-- DateTime for precision
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, related_name='created_tasks')
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)

    assigned_students = models.ManyToManyField('Student', blank=True, related_name='tasks')
    assigned_teams    = models.ManyToManyField('Team', blank=True, related_name='tasks')
    assigned_category = models.ForeignKey(Category, null=True, blank=True,
                                          on_delete=models.SET_NULL, related_name='tasks')

    github_repo   = models.URLField(blank=True, null=True)       # template link (optional)


# CHANGED — richer submission info & uniqueness guard
class TaskSubmission(models.Model):
    task            = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student         = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission_link = models.URLField()
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at     = models.DateTimeField(null=True, blank=True)
    reviewer        = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                        related_name='reviews')

    class ReviewStatus(models.TextChoices):
        SATISFIED = 'Satisfied', 'Satisfied'
        UNSATISFIED = 'Unsatisfied', 'Unsatisfied'
        TRY_AGAIN = 'Try Again', 'Try Again'

    review_status   = models.CharField(max_length=15,
                                       choices=ReviewStatus.choices,
                                       default=ReviewStatus.TRY_AGAIN)
    feedback        = models.TextField(blank=True)

    class Meta:
        unique_together = ('task', 'student')


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



# NEW — certificate / report placeholder
class Certificate(models.Model):
    student    = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    file       = models.FileField(upload_to='certificates/')
    issued_at  = models.DateField(auto_now_add=True)
    signed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='signed_certificates')

# NEW — notifications for message/task/review events
class Notification(models.Model):
    target         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    verb           = models.CharField(max_length=50)  # e.g. "new_message", "task_reviewed"
    object_id      = models.PositiveIntegerField(null=True, blank=True)
    description    = models.TextField(blank=True)
    is_read        = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)



class Certificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='certificates/')
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now) 
