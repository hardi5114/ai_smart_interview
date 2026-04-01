import json
import uuid

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required

from openai import OpenAI

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import InterviewResult, InterviewResponse


# ================= OPENAI CLIENT =================
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# =====================================================
# 🔐 DAY 4: SECURE AUDIO/VIDEO STORAGE (FIXED VERSION)
# =====================================================
@login_required
def save_response(request):
    if request.method == "POST":

        question = request.POST.get("question", "")
        audio = request.FILES.get("audio")
        video = request.FILES.get("video")

        # 🔐 Create secure unique filenames
        audio_path = None
        video_path = None

        if audio:
            audio_name = f"{uuid.uuid4()}_{audio.name}"
            audio.name = audio_name
            audio_path = audio

        if video:
            video_name = f"{uuid.uuid4()}_{video.name}"
            video.name = video_name
            video_path = video

        # 💾 Save in DB (MEDIA folder automatically handled by Django model)
        InterviewResponse.objects.create(
            user=request.user,
            question=question,
            audio_file=audio_path,
            video_file=video_path
        )

        return JsonResponse({
            "status": "success",
            "message": "Response saved securely"
        })

    return JsonResponse({"status": "invalid request"}, status=400)


# =====================================================
# 🧠 EXPERIENCE BASED QUESTION PLAN
# =====================================================
def get_question_plan(experience):
    if experience == 0:
        return {"BASIC": 3, "HR": 3, "TECH": 4}
    elif experience <= 3:
        return {"BASIC": 2, "HR": 2, "TECH": 3}
    else:
        return {"BASIC": 1, "HR": 1, "TECH": 3}


# =====================================================
# 🧠 AI QUESTION GENERATOR
# =====================================================
def generate_ai_question(user, round_type):

    results = InterviewResult.objects.filter(user=user)

    history = ""
    for r in results:
        history += f"Q: {r.question}\nA: {r.answer}\nScore: {r.score}\n\n"

    role_map = {
        "BASIC": "Ask simple interview questions.",
        "HR": "Ask HR and behavioral questions.",
        "TECH": "Ask Python and Django technical questions."
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": role_map.get(round_type, "Ask interview questions")},
                {"role": "user", "content": history + "\nAsk next question"}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("AI Question Error:", e)
        return "Tell me about yourself."


# =====================================================
# 🧠 AI SCORING ENGINE
# =====================================================
def ai_score_answer(question, answer):

    try:
        prompt = f"""
Return ONLY JSON.

Question: {question}
Answer: {answer}

Format:
{{
  "score": 0-10,
  "feedback": "short feedback"
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are strict JSON evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print("AI ERROR:", e)
        return {"score": 0, "feedback": "AI failed to evaluate answer"}


# =====================================================
# 🎥 START INTERVIEW
# =====================================================
@login_required
def start_interview(request):
    round_type = request.GET.get("round", "BASIC")
    experience = int(request.GET.get("exp", 0))

    request.session["round"] = round_type
    request.session["experience"] = experience
    request.session["round_count"] = 0

    return render(request, "interview/start_interview.html", {
        "round": round_type
    })


# =====================================================
# 🔁 NEXT QUESTION
# =====================================================
@login_required
def next_question(request):

    round_type = request.session.get("round", "BASIC")
    experience = request.session.get("experience", 0)
    round_count = request.session.get("round_count", 0)

    plan = get_question_plan(experience)

    if round_count >= plan[round_type]:
        request.session["round_count"] = 0
        return JsonResponse({"finished_round": True})

    question = generate_ai_question(request.user, round_type)

    request.session["round_count"] = round_count + 1

    return JsonResponse({
        "question": question,
        "current": round_count + 1,
        "total": plan[round_type]
    })


# =====================================================
# 📤 UPLOAD ANSWER + AI SCORING
# =====================================================
@login_required
def upload_video(request):

    if request.method == "POST":

        transcript = request.POST.get("transcript", "")
        question = request.POST.get("question", "")

        ai_result = ai_score_answer(question, transcript)

        score = ai_result.get("score", 0)
        feedback = ai_result.get("feedback", "")

        confidence = min(len(transcript) // 2, 100)
        communication = min(len(transcript.split()) * 2, 100)

        InterviewResult.objects.create(
            user=request.user,
            question=question,
            answer=transcript,
            confidence=confidence,
            communication=communication,
            accuracy=score * 10,
            score=score * 10,
            feedback=feedback,
            emotion="Neutral",
            round=request.session.get("round", "BASIC")
        )

        return JsonResponse({
            "score": score * 10,
            "feedback": feedback
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


# =====================================================
# 📊 DASHBOARD
# =====================================================
@login_required
def dashboard(request):

    results = InterviewResult.objects.filter(user=request.user)

    labels = [f"Q{i+1}" for i in range(results.count())]
    scores = [r.score for r in results]
    confidence_data = [r.confidence for r in results]
    clarity_data = [r.communication for r in results]

    last = results.last()

    if last:
        if last.score >= 80:
            badge = "🏆 Expert"
        elif last.score >= 60:
            badge = "🥈 Intermediate"
        else:
            badge = "🥉 Beginner"
    else:
        badge = "No Data"

    return render(request, "dashboard.html", {
        "labels": json.dumps(labels),
        "scores": json.dumps(scores),
        "confidence_data": json.dumps(confidence_data),
        "clarity_data": json.dumps(clarity_data),
        "ai_feedback": last.feedback if last else "",
        "badge": badge
    })


# =====================================================
# 📜 HISTORY
# =====================================================
@login_required
def history(request):
    results = InterviewResult.objects.filter(user=request.user).order_by('-id')
    return render(request, "interview/history.html", {"results": results})


# =====================================================
# 📊 RESULT PAGE
# =====================================================
@login_required
def result(request):

    results = InterviewResult.objects.filter(user=request.user)

    overall = (
        sum(r.score for r in results) // results.count()
        if results.exists() else 0
    )

    return render(request, "interview/result.html", {
        "results": results,
        "overall": overall
    })


# =====================================================
# 📄 PDF DOWNLOAD
# =====================================================
@login_required
def download_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Interview Report", styles['Title']))
    elements.append(Spacer(1, 20))

    results = InterviewResult.objects.filter(user=request.user)

    for r in results:
        elements.append(Paragraph(f"Question: {r.question}", styles['Normal']))
        elements.append(Paragraph(f"Answer: {r.answer}", styles['Normal']))
        elements.append(Paragraph(f"Score: {r.score}", styles['Normal']))
        elements.append(Spacer(1, 15))

    doc.build(elements)

    return response