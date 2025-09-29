# utils/audit_parser.py
import os
import json
import re
import logging
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text_from_pdf(pdf_path: str):
    """Extracts text from a PDF using pdfplumber only (no OCR)."""
    extracted_text = ""
    logger.info(f"🔍 Starting PDF text extraction: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"📄 Found {len(pdf.pages)} pages in PDF")
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    logger.info(f"✅ Page {i}: extracted {len(text)} characters")
                    extracted_text += text + "\n"
                else:
                    logger.warning(f"⚠️ Page {i}: no text found")
    except Exception as e:
        logger.error(f"❌ pdfplumber failed: {e}")
        return ""

    # Clean text
    extracted_text = re.sub(r'\s+', ' ', extracted_text)
    extracted_text = re.sub(r'[^\w\s.?]', ' ', extracted_text)

    logger.info(f"📊 Total text length: {len(extracted_text)} characters")
    if len(extracted_text) < 20:
        logger.warning("⚠️ Very little text was extracted. The PDF may be scanned (image-only).")

    return extracted_text.strip()


def process_text_with_openai(full_text: str):
    """Send extracted text to OpenAI for checklist generation."""
    logger.info(f"🤖 Sending {len(full_text)} characters to OpenAI...")
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
        logger.info(f"✅ Received OpenAI response ({len(result)} characters)")
        return json.loads(result)
    except Exception as e:
        logger.error(f"❌ OpenAI processing failed: {e}")
        return None


def parse_audit_pdf_openai(pdf_path: str):
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        logger.error("❌ No text could be extracted from PDF")
        return None
    return process_text_with_openai(full_text)
