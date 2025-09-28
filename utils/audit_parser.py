# utils/audit_parser.py
import os
import json
import re
import datetime
import hashlib
import logging
from typing import Optional, Dict, Any
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

# Cache for processed PDFs to avoid re-processing the same files
_processed_cache: Dict[str, Dict[str, Any]] = {}
_cache_max_size = 50



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

def get_file_hash(file_path: str) -> str:
    """Get hash of file to detect changes"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def cleanup_cache():
    """Remove old entries from cache if it gets too large"""
    global _processed_cache
    if len(_processed_cache) > _cache_max_size:
        # Remove oldest 10 entries
        oldest_keys = sorted(_processed_cache.keys(), key=lambda k: _processed_cache[k].get('timestamp', 0))[:10]
        for key in oldest_keys:
            del _processed_cache[key]
        logger.info(f"Cleaned up cache, removed {len(oldest_keys)} old entries")

def extract_text_from_pdf_optimized(pdf_path: str) -> str:
    """Optimized text extraction with better error handling"""
    cache_key = f"text_{get_file_hash(pdf_path)}"

    # Check cache first
    if cache_key in _processed_cache:
        cached_data = _processed_cache[cache_key]
        if datetime.datetime.now().timestamp() - cached_data.get('timestamp', 0) < 3600:  # 1 hour cache
            logger.info(f"Using cached text extraction for {pdf_path}")
            return cached_data['text']

    extracted_text = ""

    # Try OCR first (better for scanned documents)
    try:
        logger.info(f"Attempting OCR text extraction for {pdf_path}")
        images = convert_from_path(pdf_path, dpi=150)  # Lower DPI for speed
        for i, img in enumerate(images):
            if i > 10:  # Limit pages to prevent extremely long processing
                logger.warning(f"Stopping OCR at page {i+1}, too many pages")
                break
            text = pytesseract.image_to_string(img)
            if text.strip():
                extracted_text += text + "\n"
    except Exception as e:
        logger.warning(f"OCR failed: {e}")

    # If OCR didn't yield much text, try direct extraction
    if not extracted_text.strip() or len(extracted_text.strip()) < 100:
        try:
            logger.info(f"Attempting direct text extraction for {pdf_path}")
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    if i > 20:  # Limit pages
                        logger.warning(f"Stopping direct extraction at page {i+1}, too many pages")
                        break
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
        except Exception as e:
            logger.error(f"Direct text extraction failed: {e}")

    # Clean up the text
    extracted_text = re.sub(r'\s+', ' ', extracted_text)
    extracted_text = re.sub(r'[^\w\s.?]', ' ', extracted_text)

    # Cache the result
    _processed_cache[cache_key] = {
        'text': extracted_text.strip(),
        'timestamp': datetime.datetime.now().timestamp()
    }
    cleanup_cache()

    return extracted_text.strip()

def process_text_with_openai_optimized(full_text: str, text_hash: str) -> Optional[Dict[str, Any]]:
    """Optimized OpenAI processing with caching"""
    cache_key = f"openai_{text_hash}"

    # Check cache first
    if cache_key in _processed_cache:
        cached_data = _processed_cache[cache_key]
        if datetime.datetime.now().timestamp() - cached_data.get('timestamp', 0) < 7200:  # 2 hour cache
            logger.info("Using cached OpenAI processing result")
            return cached_data['result']

    # Truncate text if too long to avoid token limits
    if len(full_text) > 12000:  # Roughly 3000 tokens
        logger.warning(f"Text too long ({len(full_text)} chars), truncating")
        full_text = full_text[:12000] + "..."

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
        logger.info("Processing text with OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a safety audit expert. Convert safety guidelines into structured audit checklists. Return ONLY JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        result = response.choices[0].message.content
        parsed_result = json.loads(result)

        # Cache the successful result
        _processed_cache[cache_key] = {
            'result': parsed_result,
            'timestamp': datetime.datetime.now().timestamp()
        }
        cleanup_cache()

        logger.info("OpenAI processing completed successfully")
        return parsed_result

    except Exception as e:
        logger.error(f"OpenAI processing failed: {e}")
        return None

def parse_audit_pdf_openai_optimized(pdf_path: str) -> Optional[Dict[str, Any]]:
    """
    Optimized PDF parsing with caching and better error handling
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return None

    try:
        # Get file hash for caching
        file_hash = get_file_hash(pdf_path)

        # Extract text with optimization
        full_text = extract_text_from_pdf_optimized(pdf_path)
        if not full_text or len(full_text) < 50:
            logger.error(f"Insufficient text extracted from {pdf_path}")
            return None

        # Process with OpenAI
        checklist = process_text_with_openai_optimized(full_text, file_hash)
        if not checklist:
            logger.error("Failed to process text with OpenAI")
            return None

        logger.info(f"Successfully processed PDF: {pdf_path}")
        return checklist

    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
        return None
