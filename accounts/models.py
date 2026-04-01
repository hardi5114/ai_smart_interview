from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# ===============================
# FILE VALIDATOR
# ===============================
def validate_file_size(file):
    max_size_mb = 2
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size should be max {max_size_mb} MB")


# ===============================
# RESUME UPLOAD MODEL
# ===============================
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='resumes/',
        validators=[validate_file_size]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"


# ===============================
# QUESTION MODEL
# ===============================
class Question(models.Model):

    FIELD_CHOICES = [
        ('software', 'Software'),
        ('banking', 'Banking'),
        ('finance', 'Finance'),
        ('medical', 'Medical'),
        ('teaching', 'Teaching'),
        ('marketing', 'Marketing'),
        ('hr', 'HR'),
    ]

    LEVEL_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    question_text = models.TextField()
    field = models.CharField(max_length=50, choices=FIELD_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    def __str__(self):
        return self.question_text[:60]


# ===============================
# ANSWER MODEL (INTERVIEW RESULT)
# ===============================
class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    text = models.TextField()

    # AI SCORE (0–100)
    score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.question_text[:30]}"


# ===============================
# RESUME EXTRACTED DATA (AI PROFILE)
# ===============================
class ResumeData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)

    skills = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)

    experience_years = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)