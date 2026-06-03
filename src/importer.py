import csv
import logging
import re
from typing import List, Dict, Any, Tuple

from .models import Lead
from .repository import LeadRepository
from .exceptions import DuplicatePhoneError

logger = logging.getLogger(__name__)

SOURCE_MAP = {
    "fb": "Facebook",
    "facebook": "Facebook",
    "ig": "Instagram",
    "insta": "Instagram",
    "instagram": "Instagram",
    "google": "Google",
    "website": "Website",
    "referral": "Referral"
}

def normalize_source(source: str) -> str:
    s = source.strip().lower()
    return SOURCE_MAP.get(s, source.strip().title()) if s else "Unknown"

def normalize_name(name: str) -> str:
    return " ".join(name.strip().split()).title()

def validate_phone(phone: str) -> bool:
    phone = phone.strip()
    if not phone:
        return False
    # Allow digits, +, -, spaces, parenthesis
    return bool(re.match(r'^[\d\+\-\(\) ]+$', phone))

class DataImporter:
    def __init__(self, repo: LeadRepository):
        self.repo = repo

    def process_file(self, input_path: str, quarantine_path: str):
        total_rows = 0
        imported = 0
        skipped = 0
        deduplicated = 0
        
        rejected_rows: List[Dict[str, Any]] = []
        seen_phones = set()
        
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Ensure required columns are present in lower case internally
            fieldnames = [f.strip().lower() for f in reader.fieldnames or []]
            
            for row in reader:
                total_rows += 1
                
                # Map row keys to lowercase for flexible matching
                mapped_row = {k.strip().lower(): v for k, v in row.items()}
                
                name_raw = mapped_row.get("name", "")
                phone_raw = mapped_row.get("phone", "")
                source_raw = mapped_row.get("source", "")
                notes_raw = mapped_row.get("notes", "")
                
                # 1. Validation & Normalization
                if not name_raw.strip():
                    rejected_rows.append({**row, "rejection_reason": "Missing Name"})
                    skipped += 1
                    continue
                
                if not validate_phone(phone_raw):
                    rejected_rows.append({**row, "rejection_reason": "Missing or Invalid Phone"})
                    skipped += 1
                    continue
                
                name = normalize_name(name_raw)
                phone = phone_raw.strip()
                source = normalize_source(source_raw)
                notes = notes_raw.strip()
                
                # 2. In-batch Deduplication
                if phone in seen_phones:
                    rejected_rows.append({**row, "rejection_reason": "Duplicate Phone in Batch"})
                    deduplicated += 1
                    continue
                
                seen_phones.add(phone)
                
                # 3. Database Insertion
                lead = Lead(name=name, phone=phone, source=source, notes=notes)
                try:
                    self.repo.create(lead)
                    imported += 1
                except DuplicatePhoneError:
                    rejected_rows.append({**row, "rejection_reason": "Duplicate Phone in Database"})
                    deduplicated += 1
                except Exception as e:
                    logger.error(f"Unexpected error importing row: {e}")
                    rejected_rows.append({**row, "rejection_reason": f"System Error: {str(e)}"})
                    skipped += 1
                    
        # Write quarantine file if there are rejected rows
        if rejected_rows:
            with open(quarantine_path, mode='w', newline='', encoding='utf-8') as qf:
                if reader.fieldnames:
                    q_fieldnames = list(reader.fieldnames) + ["rejection_reason"]
                    writer = csv.DictWriter(qf, fieldnames=q_fieldnames)
                    writer.writeheader()
                    for r in rejected_rows:
                        writer.writerow(r)
        
        # Emit summary report
        print("\n--- Ingestion Reconciliation Report ---")
        print(f"Total Rows Processed : {total_rows}")
        print(f"Successfully Imported: {imported}")
        print(f"Skipped (Invalid)    : {skipped}")
        print(f"De-duplicated        : {deduplicated}")
        print(f"---------------------------------------")
        if rejected_rows:
            print(f"Quarantined rows written to: {quarantine_path}\n")
        
        return {
            "total": total_rows,
            "imported": imported,
            "skipped": skipped,
            "deduplicated": deduplicated
        }
