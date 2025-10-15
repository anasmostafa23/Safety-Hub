import re
import json
import os
import unicodedata
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from keybert import KeyBERT

# --- Initialize KeyBERT (unsupervised keyword extractor) ---
kw_model = KeyBERT()

# --- Helpers ---
def slugify(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '_', text).strip('_')
    return text

def normalize_answer(ans: str) -> str:
    ans = ans.strip().upper()
    if ans in ["YES", "Y"]: return "YES"
    if ans in ["NO", "N"]: return "NO"
    if ans in ["N/A", "NA", "NOT APPLICABLE"]: return "N/A"
    return "N/A"

def extract_keyword(question: str) -> str:
    """Use KeyBERT to extract 1-2 word keyword from the question."""
    try:
        keywords = kw_model.extract_keywords(
            question, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='english',
            top_n=1
        )
        if keywords:
            return slugify(keywords[0][0])
    except Exception as e:
        print(f"[!] Keyword extraction failed for: {question} -> {e}")
    return slugify(question[:5])  # fallback: first 5 chars

def parse_audit_text(text: str):
    checklist = []
    for line in text.splitlines():
        line = line.strip()
        # Match lines like "Question? Answer"
        match = re.match(r"(.+?\?)\s*(Yes|No|N/A)$", line, re.IGNORECASE)
        if match:
            question = match.group(1).strip()
            answer = normalize_answer(match.group(2))
            keyword = extract_keyword(question)
            checklist.append({
                "question": question,
                "keyword": keyword,
                "options": ["YES", "NO", "N/A"],
                "detected_answer": answer
            })
    return checklist

# --- Main Parser ---
def parse_audit_pdf(pdf_path: str):
    checklist = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            print("PAGE TEXT:\n", text)
            if text:
                checklist.extend(parse_audit_text(text))

    # If nothing useful → OCR
    if not checklist:
        print("[!] No text found. Running OCR...")
        images = convert_from_path(pdf_path)
        for img in images:
            text = pytesseract.image_to_string(img)
            checklist.extend(parse_audit_text(text))

    return checklist

def save_checklist(checklist, output_folder="checklists", filename="parsed_checklist.json"):
    os.makedirs(output_folder, exist_ok=True)
    path = os.path.join(output_folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)
    print(f"[+] Checklist saved to {path}")

# --- Usage ---
if __name__ == "__main__":
    pdf_file = "/home/mx/workspace/github.com/anasmostafa23/Safety-Hub/exports/audit_Momen_20250523_024907.pdf"
    checklist = parse_audit_pdf(pdf_file)
    save_checklist(checklist)
