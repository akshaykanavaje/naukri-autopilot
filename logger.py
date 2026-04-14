# ============================================================
#  logger.py  —  Tracks all applications and saves job lists
# ============================================================

import csv
import os
from datetime import datetime

APPLIED_FILE   = "applied_jobs.csv"
MANUAL_FILE    = "manual_apply.csv"
QUESTIONS_FILE = "questions_jobs.csv"

APPLIED_FIELDS   = ["job_id", "title", "company", "experience", "location", "group", "applied_at"]
MANUAL_FIELDS    = ["job_id", "title", "company", "experience", "location", "job_url", "group", "saved_at"]
QUESTIONS_FIELDS = ["job_id", "title", "company", "experience", "location", "job_url", "group", "saved_at"]

_seen_ids: set = set()

def _load_ids_from(filepath: str) -> set:
    if not os.path.exists(filepath):
        return set()
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["job_id"] for row in reader if "job_id" in row}

_seen_ids = (
    _load_ids_from(APPLIED_FILE)
    | _load_ids_from(MANUAL_FILE)
    | _load_ids_from(QUESTIONS_FILE)
)

def already_applied(job_id: str) -> bool:
    return job_id in _seen_ids

def _write_row(filepath: str, fieldnames: list, row: dict) -> None:
    try:
        exists = os.path.exists(filepath)
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not exists:
                writer.writeheader()
            writer.writerow(row)
        _seen_ids.add(row["job_id"])
    except Exception as e:
        print(f"  ⚠️  CSV write error ({filepath}): {e}")

def log_application(job_id: str, title: str, company: str,
                    experience: str, location: str, group: str) -> None:
    _write_row(APPLIED_FILE, APPLIED_FIELDS, {
        "job_id":     job_id,
        "title":      title,
        "company":    company,
        "experience": experience,
        "location":   location,
        "group":      group,
        "applied_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

def log_manual(job_id: str, title: str, company: str, experience: str,
               location: str, job_url: str, group: str) -> None:
    _write_row(MANUAL_FILE, MANUAL_FIELDS, {
        "job_id":     job_id,
        "title":      title,
        "company":    company,
        "experience": experience,
        "location":   location,
        "job_url":    job_url,
        "group":      group,
        "saved_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

def log_questions(job_id: str, title: str, company: str, experience: str,
                  location: str, job_url: str, group: str) -> None:
    _write_row(QUESTIONS_FILE, QUESTIONS_FIELDS, {
        "job_id":     job_id,
        "title":      title,
        "company":    company,
        "experience": experience,
        "location":   location,
        "job_url":    job_url,
        "group":      group,
        "saved_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    })