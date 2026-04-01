from django.db import models
from django.contrib.auth.models import User


# ==============================
# 🎯 ROUND CHOICES
# ==============================
ROUND_CHOICES = [
    ("BASIC", "Basic"),
    ("HR", "HR"),
    ("TECH", "Technical"),
]


# ==============================
# 👤 PROFILE (RESUME STORAGE)
# ==============================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    def __str__(self):
        return self.user.username


# ==============================
# 🎥 SECURE MEDIA RESPONSE STORAGE
# ==============================
class InterviewResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    question = models.TextField()

    # secure media storage paths
    audio_file = models.FileField(upload_to='responses/audio/', null=True, blank=True)
    video_file = models.FileField(upload_to='responses/video/', null=True, blank=True)

    round = models.CharField(max_length=10, choices=ROUND_CHOICES, default="BASIC")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Response {self.id}"


# ==============================
# 🧠 AI SCORE LOG (OPTIONAL LOGGING)
# ==============================
class InterviewScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    question = models.TextField()
    answer = models.TextField()

    score = models.FloatField(default=0)
    feedback = models.TextField()

    round = models.CharField(max_length=10, choices=ROUND_CHOICES, default="BASIC")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Score {self.score}"


# ==============================
# 📊 FINAL RESULT (MAIN DASHBOARD DATA)
# ==============================
class InterviewResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    question = models.TextField()
    answer = models.TextField()

    confidence = models.IntegerField(default=0)
    communication = models.IntegerField(default=0)
    accuracy = models.IntegerField(default=0)

    score = models.IntegerField(default=0)
    grade = models.CharField(max_length=5, default="F")

    feedback = models.TextField(default="")
    emotion = models.CharField(max_length=50, default="Neutral")

    round = models.CharField(max_length=10, choices=ROUND_CHOICES, default="BASIC")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.round} - {self.score}"