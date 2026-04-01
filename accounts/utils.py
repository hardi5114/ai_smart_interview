import pdfplumber
import docx
import re


# Extract text from PDF
def extract_pdf_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


# Extract text from DOCX
def extract_docx_text(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])


# Detect sections (basic logic)
def parse_resume(text):

    skills = []
    education = []
    experience = []

    lines = text.lower().split("\n")

    for line in lines:
        if "python" in line or "django" in line or "sql" in line:
            skills.append(line)

        if "bachelor" in line or "degree" in line:
            education.append(line)

        if "year" in line or "experience" in line:
            experience.append(line)

    return {
        "skills": ", ".join(skills),
        "education": ", ".join(education),
        "experience": ", ".join(experience),
    }