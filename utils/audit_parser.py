# utils/audit_parser.py
import os
import json
import re
import datetime
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def extract_text_from_pdf(pdf_path: str):
    extracted_text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text = pytesseract.image_to_string(img)
            if text.strip():
                extracted_text += text + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")

    if not extracted_text.strip():
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}")

    extracted_text = re.sub(r'\s+', ' ', extracted_text)
    extracted_text = re.sub(r'[^\w\s.?]', ' ', extracted_text)
    return extracted_text.strip()

def process_text_with_openai(full_text: str):
    prompt = f"""
Convert the following safety guidelines text into a structured JSON safety audit checklist.

TEXT TO PROCESS:
{full_text}

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON, no other text
- for keyword field write the keyword in this format "keyword": "short_snake_case_id/key_word_in_Russian"
- make the response field empty
- Follow this exact structure:
{{
  "template_name": "Site Safety Audit Checklist",
  "categories": [
    {{
      "name": "Category Name",
      "questions": [
        {{
          "keyword": "short_snake_case_id/key_word_in_Russian",
          "question_en": "Clear safety audit question",
          "question_ru": "Очищенный вопрос безопасности",
          "response": "",
          "options": ["Yes", "No", "N/A"]
        }}
      ]
    }}
  ]
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a safety audit expert. Convert safety guidelines into structured audit checklists. Return ONLY JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        return json.loads(result)
    except Exception as e:
        print(f"OpenAI processing failed: {e}")
        return None

def parse_audit_pdf_openai(pdf_path: str):
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        return None
    checklist = process_text_with_openai(full_text)
    return checklist
