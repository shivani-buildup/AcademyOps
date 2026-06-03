import argparse
import logging
import sys

from .models import Lead, LeadStage
from .repository import LeadRepository
from .exceptions import LeadError, DuplicatePhoneError, InvalidStageError
from .db_init import init_db
from .importer import DataImporter

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("academyops.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description="AcademyOps CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init DB command
    subparsers.add_parser("initdb", help="Initialize the database schema")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new lead")
    add_parser.add_argument("--name", required=True, help="Lead's name")
    add_parser.add_argument("--phone", required=True, help="Lead's phone number")
    add_parser.add_argument("--source", help="Lead source")
    add_parser.add_argument("--notes", help="Lead notes")
    
    # List command
    subparsers.add_parser("list", help="List all leads")
    
    # Update stage command
    update_parser = subparsers.add_parser("update", help="Update a lead's stage")
    update_parser.add_argument("--id", type=int, required=True, help="Lead ID")
    update_parser.add_argument("--stage", required=True, help="New stage (New, Contacted, Qualified, Demo, Enrolled, Lost)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a lead")
    delete_parser.add_argument("--id", type=int, required=True, help="Lead ID")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import leads from a CSV file")
    import_parser.add_argument("--file", required=True, help="Path to input CSV file")
    import_parser.add_argument("--quarantine", default="data/quarantine.csv", help="Path to write quarantined rows")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    repo = LeadRepository()
    
    try:
        if args.command == "initdb":
            init_db()
            print("Database initialized.")
            
        elif args.command == "add":
            lead = Lead(name=args.name, phone=args.phone, source=args.source, notes=args.notes)
            created_lead = repo.create(lead)
            print(f"Success! Created Lead ID: {created_lead.id}")
            
        elif args.command == "list":
            leads = repo.list()
            if not leads:
                print("No leads found.")
            else:
                print(f"{'ID':<5} | {'Name':<20} | {'Phone':<15} | {'Stage':<12} | {'Source':<15}")
                print("-" * 75)
                for l in leads:
                    source = l.source if l.source else 'N/A'
                    print(f"{l.id:<5} | {l.name:<20} | {l.phone:<15} | {l.stage.value:<12} | {source:<15}")
                    
        elif args.command == "update":
            updated_lead = repo.update_stage(args.id, args.stage)
            print(f"Success! Updated Lead ID {updated_lead.id} to stage '{updated_lead.stage.value}'")
            
        elif args.command == "delete":
            repo.delete(args.id)
            print(f"Success! Deleted Lead ID {args.id}")
            
        elif args.command == "import":
            importer = DataImporter(repo)
            importer.process_file(args.file, args.quarantine)
            
    except DuplicatePhoneError as e:
        logger.error(str(e))
        print(f"Error: A lead with this phone number already exists.")
        sys.exit(1)
    except InvalidStageError as e:
        logger.error(str(e))
        print(f"Error: Invalid stage provided. Allowed stages: {[s.value for s in LeadStage]}")
        sys.exit(1)
    except LeadError as e:
        logger.error(str(e))
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
