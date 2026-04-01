import json
import re
import pdfplumber
import pytesseract

from pdf2image import convert_from_path

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

from .models import Resume, ResumeData, Answer

import openai

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

# 📄 PDF TEXT EXTRACTION
def extract_text_pdf(file_path):
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        return text.strip()
    except:
        return ""

# 👁️ OCR (SCANNED PDF)
def extract_text_ocr(file_path):
    try:
        images = convert_from_path(file_path)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
        return text.strip()
    except:
        return ""
 
# ⚡ HYBRID EXTRACTOR
def extract_resume_text(file_path):
    text = extract_text_pdf(file_path)

    if not text or len(text) < 50:
        text = extract_text_ocr(file_path)

    return text

# 🧠 REGEX FALLBACK (SMART FIX)
def extract_with_regex(text):

    # EMAIL
    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    email = email[0] if email else ""

    # NAME (first line logic)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    full_name = lines[0] if lines else "Not detected"

    # SKILLS
    skills = ""
    if "SKILLS" in text.upper():
        try:
            skills = text.upper().split("SKILLS")[1].split("EDUCATION")[0]
        except:
            skills = ""

    # EDUCATION
    education = ""
    if "EDUCATION" in text.upper():
        try:
            education = text.upper().split("EDUCATION")[1].split("PROJECT")[0]
        except:
            education = ""

    return {
        "full_name": full_name.title(),
        "email": email,
        "skills": skills[:300],
        "education": education[:300],
        "experience": "",
        "experience_years": 0
    }


# =====================================================
# 🧠 AI PARSER (IMPROVED PROMPT)
# =====================================================
def extract_resume_data_ai(text):
    try:
        if not text:
            return None

        text = text[:4000]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Extract structured resume data strictly in JSON. No explanation."
                },
                {
                    "role": "user",
                    "content": f"""
Extract clean structured data from resume.

Return ONLY JSON:

{{
  "full_name": "",
  "email": "",
  "skills": "comma separated",
  "education": "",
  "experience": "",
  "experience_years": 0
}}

Rules:
- Extract correct email
- Extract real skills only (not paragraph)
- Extract education clearly
- Do NOT include extra text

Resume:
{text}
"""
                }
            ],
            temperature=0
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "")

        data = json.loads(raw)

        return data

    except Exception as e:
        print("AI ERROR:", e)
        return None


# =====================================================
# 🏠 REGISTER
# =====================================================
def register_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("accounts:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("accounts:register")

        User.objects.create_user(username=username, email=email, password=password)
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


# =====================================================
# 🔐 LOGIN
# =====================================================
def login_view(request):
    if request.method == "POST":

        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect("accounts:dashboard")

        messages.error(request, "Invalid login")

    return render(request, "accounts/login.html")


# =====================================================
# 🚪 LOGOUT
# =====================================================
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# =====================================================
# 📊 DASHBOARD
# =====================================================
@login_required
def dashboard(request):

    resume = Resume.objects.filter(user=request.user).last()
    data = ResumeData.objects.filter(user=request.user).last()

    return render(request, "accounts/dashboard.html", {
        "resume": resume,
        "resume_data": data
    })


# =====================================================
# 📤 UPLOAD RESUME (🔥 FINAL FIXED PIPELINE)
# =====================================================
@login_required
def upload_resume(request):

    if request.method == "POST":

        file = request.FILES.get("resume")

        if not file:
            return render(request, "accounts/upload_resume.html", {
                "message": "❌ No file uploaded"
            })

        resume = Resume.objects.create(user=request.user, file=file)
        file_path = resume.file.path

        # 🔍 Extract text
        text = extract_resume_text(file_path)

        if not text:
            return render(request, "accounts/upload_resume.html", {
                "message": "❌ Could not read resume"
            })

        # 🧠 Try AI
        data = extract_resume_data_ai(text)

        # 🛡 Fallback (VERY IMPORTANT)
        if not data:
            data = extract_with_regex(text)

        # 💾 Save clean data
        ResumeData.objects.update_or_create(
            user=request.user,
            defaults={
                "full_name": data.get("full_name", "Not detected"),
                "email": data.get("email", ""),
                "skills": data.get("skills", ""),
                "education": data.get("education", ""),
                "experience": data.get("experience", ""),
                "experience_years": int(data.get("experience_years", 0) or 0),
            }
        )

        return render(request, "accounts/upload_resume.html", {
            "message": "✅ Resume processed successfully"
        })

    return render(request, "accounts/upload_resume.html")


# =====================================================
# 🎤 INTERVIEW
# =====================================================
@login_required
def start_interview(request):
    return render(request, "accounts/start_interview.html")


@login_required
def video_interview(request):
    return render(request, "accounts/video_interview.html")


# =====================================================
# 💾 SAVE ANSWERS
# =====================================================
@login_required
def save_answer_ajax(request):

    if request.method == "POST":

        data = json.loads(request.body)

        ans = Answer.objects.create(
            user=request.user,
            question_id=data.get("question_id"),
            text=data.get("answer")
        )

        return JsonResponse({"status": "saved", "id": ans.id})

    return JsonResponse({"status": "error"})