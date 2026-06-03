# AcademyOps: End-to-End System Case Study

## Executive Summary
AcademyOps is a robust, data-driven Lead-to-Enrollment Management System built for the EasySkill Career Academy (ECA). This case study walks through the entire lifecycle of a lead interacting with the system—from ingestion to enrollment—demonstrating the system's resilience, automation, and analytics capabilities.

## 1. Data Ingestion & Cleansing (The Beginning)
Our story begins when ECA acquires a list of marketing leads in a messy CSV format (`data/messy_leads.csv`). These leads have missing names, malformed phone numbers, and inconsistent source tags.
- **The Process:** A counselor runs our custom Python Importer (`scripts/importer.py`).
- **The Magic:** The pipeline automatically standardizes phone numbers to a strict format (e.g., `+91-XXXXX`), maps unknown sources to "Unknown", and drops invalid entries into a `quarantine.csv` file for manual review.
- **Result:** Only pristine, validated leads enter our system.

## 2. API Routing & Storage (The Backend)
Once the lead is clean, it is sent to our modern **FastAPI** backend (`src/main.py`).
- **Validation:** Pydantic rigorously validates the incoming JSON payload (`src/schemas.py`). If a lead is submitted without a name, FastAPI instantly rejects it with a 422 Unprocessable Entity error.
- **Persistence:** The lead is securely saved into a **PostgreSQL** database using SQLAlchemy (`src/database.py`). It is assigned an initial stage of `"New"`.

## 3. Intelligent Intent Classification (The Automation)
Suppose a newly acquired lead replies to an automated text message, asking: *"What is the fee structure for the evening batch?"*
- **The Process:** The message is POSTed to our Intelligence Layer (`/api/v1/leads/{id}/message`).
- **The Magic:** Our `RuleBasedClassifier` (`src/classifier.py`) scans the message. It detects keywords like *"fee"* and identifies the intent as `"fees"`. 
- **The Automation:** The system automatically responds with a templated message explaining the fees, and instantly updates the lead's database stage from `"New"` to `"Contacted"`. The counselor saved 10 minutes of manual data entry!

## 4. Analytics & Visualization (The Dashboard)
At the end of the week, the Admissions Director wants to review performance.
- **The Process:** They launch the **Streamlit Operations Dashboard** (`src/dashboard.py`).
- **The Insight:** The dashboard pulls the live data using Pandas and renders a beautiful Funnel Chart using Altair. The director can instantly see that out of 100 `"New"` leads, 40 reached `"Contacted"`, but only 5 reached `"Enrolled"`.
- **The Action:** Using the interactive sidebar, they filter by "Facebook" leads and notice the drop-off is severe at the "Demo" stage, indicating a need for better demo presentations.

## Conclusion
Through automated data cleansing (WP-02), robust FastAPI architecture (WP-07), intelligent rule-based automation (WP-08), and visual analytics (WP-05 & WP-06), AcademyOps transforms a messy, manual admissions process into a streamlined, data-driven machine.
