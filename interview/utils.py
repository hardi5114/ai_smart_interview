import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY
import uuid

def unique_filename(instance, filename):
    ext = filename.split('.')[-1]
    return f"{uuid.uuid4()}.{ext}"

def evaluate_answer(transcript):

    prompt = f"""
    Evaluate this interview answer professionally.

    Answer:
    {transcript}

    Give:
    - Score out of 10
    - Strengths
    - Weaknesses
    - Improvement Tips
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]


def calculate_confidence(eye_score, emotion_score, speech_score):

    confidence = (
        eye_score * 0.4 +
        emotion_score * 0.3 +
        speech_score * 0.3
    )

    return round(confidence)