import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_db(db_path: str = "data/academyops.db"):
    """Initialize the SQLite database schema."""
    logger.info(f"Initializing database at {db_path}")
    
    schema = """
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        source TEXT,
        stage TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    
    CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);
    CREATE INDEX IF NOT EXISTS idx_leads_stage ON leads(stage);
    """
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.executescript(schema)
            logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
