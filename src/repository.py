import sqlite3
import logging
from datetime import datetime, timezone
from typing import List, Optional

from .models import Lead, LeadStage
from .exceptions import LeadNotFound, DuplicatePhoneError, InvalidStageError

logger = logging.getLogger(__name__)

class LeadRepository:
    def __init__(self, db_path: str = "data/academyops.db"):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, lead: Lead) -> Lead:
        now = datetime.now(timezone.utc).isoformat()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO leads (name, phone, source, stage, notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (lead.name, lead.phone, lead.source, lead.stage.value, lead.notes, now, now)
                )
                lead.id = cursor.lastrowid
                lead.created_at = now
                lead.updated_at = now
                logger.info(f"Created lead {lead.id} with phone {lead.phone}")
                return lead
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to create lead due to integrity error: {e}")
            if "UNIQUE constraint failed: leads.phone" in str(e):
                raise DuplicatePhoneError(f"Lead with phone {lead.phone} already exists.")
            raise

    def get(self, lead_id: int) -> Lead:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Lead with id {lead_id} not found.")
                raise LeadNotFound(f"Lead with id {lead_id} not found.")
                
            return self._row_to_lead(row)

    def list(self, stage: Optional[str] = None, source: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Lead]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM leads WHERE 1=1"
            params = []
            
            if stage:
                query += " AND stage = ?"
                params.append(stage)
                
            if source:
                query += " AND source = ?"
                params.append(source)
                
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_lead(row) for row in rows]

    def update_stage(self, lead_id: int, new_stage: LeadStage) -> Lead:
        if not isinstance(new_stage, LeadStage):
            try:
                new_stage = LeadStage(new_stage)
            except ValueError:
                raise InvalidStageError(f"Invalid stage: {new_stage}")

        now = datetime.now(timezone.utc).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE leads
                SET stage = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_stage.value, now, lead_id)
            )
            
            if cursor.rowcount == 0:
                logger.warning(f"Failed to update stage: Lead {lead_id} not found.")
                raise LeadNotFound(f"Lead with id {lead_id} not found.")
            
            logger.info(f"Updated lead {lead_id} stage to {new_stage.value}")
            
        return self.get(lead_id)

    def delete(self, lead_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"Failed to delete: Lead {lead_id} not found.")
                raise LeadNotFound(f"Lead with id {lead_id} not found.")
                
            logger.info(f"Deleted lead {lead_id}")

    def _row_to_lead(self, row: sqlite3.Row) -> Lead:
        return Lead(
            id=row['id'],
            name=row['name'],
            phone=row['phone'],
            source=row['source'],
            stage=LeadStage(row['stage']),
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
