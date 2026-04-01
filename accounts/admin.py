from django.contrib import admin
from .models import Resume, ResumeData, Question, Answer


# Register models in Django Admin
admin.site.register(Resume)
admin.site.register(ResumeData)
admin.site.register(Question)
admin.site.register(Answer)