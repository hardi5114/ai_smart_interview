from django.urls import path
from . import views

app_name = "interview"

urlpatterns = [
    path("start/", views.start_interview, name="start_interview"),
    path("next-question/", views.next_question, name="next_question"),
    path("upload/", views.upload_video, name="upload_video"),
    path('result/', views.result, name='result'),
    path('history/', views.history, name='history'),
    path("download-pdf/", views.download_pdf, name="download_pdf"), 
]

