from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# =========================
# LEVEL MODEL (NEW)
# =========================
class Level(models.Model):
    LEVEL_CHOICES = (
        ('Primary', 'Primary Level'),
        ('JSS', 'Junior Secondary School'),
        ('SSS', 'Senior School'),
    )

    name = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} - Ksh {self.price}"


# =========================
# GRADE MODEL (NEW)
# =========================
class Grade(models.Model):

    name = models.CharField(max_length=50)

    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    def __str__(self):
        return self.name



# =========================
# COURSE (UPDATED)
# =========================
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    # NEW FIELDS
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# =========================
# COURSE MATERIALS
# =========================
class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# ATTENDANCE
# =========================
class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.date}"


class Attendance(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.session.course.title}"


# =========================
# SUBSCRIPTION (REPLACES ENROLLMENT LOGIC)
# =========================
class Subscription(models.Model):

    student = models.ForeignKey(User, on_delete=models.CASCADE)

    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE
    )

    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    is_active = models.BooleanField(default=False)

    payment_reference = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    subscribed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.level.name}"


# =========================
# EXAMS
# =========================
class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    total_marks = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1)

    def __str__(self):
        return self.question_text


class StudentExam(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'exam')


# =========================
# LIVE SESSION
# =========================
class LiveSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    room_name = models.CharField(max_length=200, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# PAYMENT (UPDATED)
# =========================
class Payment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE)

    # 🔥 NOW LINKED TO LEVEL NOT COURSE
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.level} - {self.status}"

class Video(models.Model):

    title = models.CharField(max_length=200)

    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="videos")

    video = models.FileField(upload_to='videos/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title