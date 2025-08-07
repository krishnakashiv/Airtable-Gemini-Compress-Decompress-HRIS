import os
from dotenv import load_dotenv

load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")

# Table names
TABLE_PERSONAL = "Personal Details"
TABLE_EXPERIENCE = "Work Experience"
TABLE_SALARY = "Salary Preferences"
APPLICANTS_TABLE = "Applicants"
SHORTLISTED_TABLE = "Shortlisted Leads"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}
