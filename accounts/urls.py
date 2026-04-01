from django.urls import path
from . import views
from .models import Resume, Answer

app_name = "accounts"

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('start-interview/', views.start_interview, name='start_interview'),
    path('video-interview/', views.video_interview, name='video_interview'),
    path('save-answer/', views.save_answer_ajax, name='save_answer'),
]