from src.database import engine, Base
from src.models import LeadModel

def init_db():
    print("Creating SQLAlchemy tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
