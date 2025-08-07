from typing import List, Dict, Optional
from data_access.airtable_client import AirtableClient
import json
import logging
from config.airtable_config import (
    TABLE_PERSONAL, 
    TABLE_EXPERIENCE, 
    TABLE_SALARY, 
    APPLICANTS_TABLE, 
    SHORTLISTED_TABLE
)
from models.applicant import Applicant, PersonalInfo, WorkExperience, SalaryPreferences

logger = logging.getLogger(__name__)

class ApplicantRepository:
    """Repository for accessing applicant data from Airtable"""
    
    def __init__(self):
        self.client = AirtableClient()
    
    def get_personal_info(self, applicant_id: str) -> Optional[PersonalInfo]:
        """Get personal info for an applicant"""
        # Check if ApplicantId is numeric
        try:
            numeric_id = int(applicant_id)
            filter_formula = f"{{ApplicantId}} = {numeric_id}"
        except ValueError:
            # If not numeric, use string format
            filter_formula = f"{{ApplicantId}} = '{applicant_id}'"
        
        records = self.client.fetch_records(TABLE_PERSONAL, filter_formula)
        
        if not records:
            return None
            
        fields = records[0]["fields"]
        return PersonalInfo(
            name=fields.get("Full Name"),
            email=fields.get("Email"),
            location=fields.get("Location"),
            linkedin=fields.get("LinkedIn")
        )
    
    def get_work_experience(self, applicant_id: str) -> List[WorkExperience]:
        """Get work experience for an applicant"""
        # Check if applicant_id is numeric
        try:
            numeric_id = int(applicant_id)
            filter_formula = f"{{Personal Details}} = {numeric_id}"
        except ValueError:
            # If not numeric, use string format
            filter_formula = f"{{Personal Details}} = '{applicant_id}'"
        
        records = self.client.fetch_records(TABLE_EXPERIENCE, filter_formula)
        
        experience_list = []
        for record in records:
            fields = record["fields"]
            experience = WorkExperience(
                company=fields.get("Company"),
                title=fields.get("Title"),
                start=fields.get("Start"),
                end=fields.get("End"),
                technologies=fields.get("Technologies")
            )
            experience_list.append(experience)
            
        return experience_list
    
    def get_salary_preferences(self, applicant_id: str) -> SalaryPreferences:
        """Get salary preferences for an applicant"""
        # Check if applicant_id is numeric
        try:
            numeric_id = int(applicant_id)
            filter_formula = f"{{Personal Details}} = {numeric_id}"
        except ValueError:
            # If not numeric, use string format
            filter_formula = f"{{Personal Details}} = '{applicant_id}'"
        
        records = self.client.fetch_records(TABLE_SALARY, filter_formula)
        
        salary_data = SalaryPreferences()
        if records:
            fields = records[0]["fields"]
            salary_data = SalaryPreferences(
                preferred_rate=fields.get("Preferred Rate"),
                minimum_rate=fields.get("Minimum Rate"),
                currency=fields.get("Currency"),
                availability=fields.get("Availability (hrs/wk)")
            )
            
        return salary_data
    
    def get_applicant(self, applicant_id: str) -> Optional[Applicant]:
        """Get complete applicant data"""
        personal = self.get_personal_info(applicant_id)
        if not personal:
            return None
            
        experience = self.get_work_experience(applicant_id)
        salary = self.get_salary_preferences(applicant_id)
        
        return Applicant(personal=personal, experience=experience, salary=salary)
    
    def save_compressed_applicant(self, applicant_id: str, compressed_json: str, 
                                shortlist_status: str, llm_score: Optional[int], 
                                llm_summary: Optional[str], llm_follow_ups: Optional[str]) -> Dict:
        """Save compressed applicant data to Applicants table"""
        fields = {
            "ApplicantId": str(applicant_id),
            "Compressed JSON": compressed_json,
            "Shortlist Status": shortlist_status,
        }
        
        if llm_score is not None:
            fields["LLM Score"] = llm_score
        if llm_summary:
            fields["LLM Summary"] = llm_summary
        if llm_follow_ups:
            fields["LLM Follow Ups"] = llm_follow_ups
            
        filter_formula = f'{{ApplicantId}} = "{applicant_id}"'
        return self.client.upsert_record(APPLICANTS_TABLE, filter_formula, fields)
    
    def get_compressed_applicant(self, applicant_id: str) -> Optional[Dict]:
        """Get compressed applicant JSON from Applicants table"""
        # Check if ApplicantId is numeric
        try:
            numeric_id = int(applicant_id)
            filter_formula = f"{{ApplicantId}} = {numeric_id}"
        except ValueError:
            # If not numeric, use string format
            filter_formula = f"{{ApplicantId}} = '{applicant_id}'"
        
        records = self.client.fetch_records(APPLICANTS_TABLE, filter_formula)
        
        if not records:
            return None
            
        return records[0]
    
    def save_shortlisted_lead(self, applicant_record_id: str, compressed_json: str, reason: str) -> Dict:
        """Save shortlisted lead to Shortlisted Leads table"""
        # Fetch all records with linked Applicants
        existing_records = self.client.fetch_records(
            SHORTLISTED_TABLE, 
            f"COUNTA({{Applicants}}) > 0"
        )
        
        logger.info(f"Found {len(existing_records)} shortlisted lead records with linked Applicants")
        
        # Filter further to only get records linked to our specific applicant_record_id
        records_to_delete = []
        for record in existing_records:
            applicants_field = record.get('fields', {}).get('Applicants', [])
            if applicant_record_id in applicants_field or applicant_record_id in [str(id) for id in applicants_field]:
                records_to_delete.append(record)
                
        logger.info(f"Checking existing shortlisted records for: {applicant_record_id}")
        logger.info(f"Found: {len(records_to_delete)} records to delete")

        # Delete existing records
        for record in records_to_delete:
            record_id = record["id"]
            logger.info(f"Deleting shortlisted lead record: {record_id}")
            self.client.delete_record(SHORTLISTED_TABLE, record_id)
            
        fields = {
            "Applicants": [applicant_record_id],
            "Compressed JSON": compressed_json,
            "Score Reason": reason
        }
        
        logger.info("Creating new shortlisted lead record")
        return self.client.create_record(SHORTLISTED_TABLE, fields)
    
    def save_personal_info(self, applicant_id: str, personal_info: PersonalInfo) -> Dict:
        """Save personal info to Personal Details table"""
        fields = {
            "Full Name": personal_info.name,
            "Email": personal_info.email,
            "Location": personal_info.location,
            "LinkedIn": personal_info.linkedin
        }
        
        # Check if ApplicantId is numeric
        try:
            numeric_id = int(applicant_id)
            filter_formula = f"{{ApplicantId}} = {numeric_id}"
        except ValueError:
            # If not numeric, use string format
            filter_formula = f"{{ApplicantId}} = '{applicant_id}'"
        
        return self.client.upsert_record(TABLE_PERSONAL, filter_formula, fields)
    
    def save_work_experience(self, personal_id: str, experience_list: List[WorkExperience]) -> List[Dict]:
        """Save work experience to Work Experience table"""
        created_records = []
        
        # Clear existing records by finding records linked to this personal_id
        # Using COUNTA to check if the linked field array contains the personal_id
        existing_records = self.client.fetch_records(TABLE_EXPERIENCE, f"COUNTA({{Personal Details}}) > 0")
        logger.info(f"Found {len(existing_records)} work experience records with linked Personal Details")
        
        # Filter further to only get records linked to our specific personal_id
        records_to_delete = []
        for record in existing_records:
            personal_details_field = record.get('fields', {}).get('Personal Details', [])
            if personal_id in personal_details_field or personal_id in [str(id) for id in personal_details_field]:
                records_to_delete.append(record)
                
        logger.info(f"Found {len(records_to_delete)} existing work experience records to delete")
        for record in records_to_delete:
            logger.info(f"Deleting work experience record: {record['id']}")
            self.client.delete_record(TABLE_EXPERIENCE, record["id"])
        
        # Create new records
        for exp in experience_list:
            fields = {
                "Company": exp.company,
                "Title": exp.title,
                "Start": exp.start,
                "End": exp.end,
                "Technologies": exp.technologies,
                "Personal Details": [personal_id]
            }
            
            record = self.client.create_record(TABLE_EXPERIENCE, fields)
            created_records.append(record)
            
        logger.info(f"Cleared and created {len(created_records)} work experience record(s).")
        return created_records
    
    def save_salary_preferences(self, personal_id: str, salary_data: SalaryPreferences) -> Dict:
        """Save salary preferences to Salary Preferences table"""
        fields = {
            "Preferred Rate": salary_data.preferred_rate,
            "Minimum Rate": salary_data.minimum_rate,
            "Currency": salary_data.currency,
            "Availability (hrs/wk)": salary_data.availability,
            "Personal Details": [personal_id]
        }
        
        # Clear existing records by finding records linked to this personal_id
        # Using COUNTA to check if the linked field array contains the personal_id
        existing_records = self.client.fetch_records(TABLE_SALARY, f"COUNTA({{Personal Details}}) > 0")
        logger.info(f"Found {len(existing_records)} salary preference records with linked Personal Details")
        
        # Filter further to only get records linked to our specific personal_id
        records_to_delete = []
        for record in existing_records:
            personal_details_field = record.get('fields', {}).get('Personal Details', [])
            if personal_id in personal_details_field or personal_id in [str(id) for id in personal_details_field]:
                records_to_delete.append(record)
                
        logger.info(f"Found {len(records_to_delete)} existing salary preference records to delete")
        for record in records_to_delete:
            logger.info(f"Deleting salary preference record: {record['id']}")
            self.client.delete_record(TABLE_SALARY, record["id"])
        
        logger.info(f"Cleared {len(existing_records)} salary preference record(s).")
        
        return self.client.create_record(TABLE_SALARY, fields)
        
        # # Filter further to only get records linked to our specific personal_id
        # records_to_delete = []
        # for record in existing_records:
        #     personal_details_field = record.get('fields', {}).get('Personal Details', [])
        #     if personal_id in personal_details_field or personal_id in [str(id) for id in personal_details_field]:
        #         records_to_delete.append(record)
                
        # logger.info(f"Found {len(records_to_delete)} existing salary preference records to delete")
        # for record in records_to_delete:
        #     logger.info(f"Deleting salary preference record: {record['id']}")
        #     self.client.delete_record(TABLE_SALARY, record["id"])
        
        # logger.info(f"Cleared {len(existing_records)} salary preference record(s).")
        
        # return self.client.create_record(TABLE_SALARY, fields)
