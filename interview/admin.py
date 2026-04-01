from django.contrib import admin
from .models import Profile, InterviewResult


# ✅ Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "resume")


# ✅ Interview Result Admin
@admin.register(InterviewResult)
class InterviewResultAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "grade", "round", "created_at")
    list_filter = ("round", "grade")
    search_fields = ("user__username",)