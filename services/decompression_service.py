import json
import logging
from typing import Dict, Any
from data_access.applicant_repository import ApplicantRepository
from models.applicant import PersonalInfo, WorkExperience, SalaryPreferences

logger = logging.getLogger(__name__)


class DecompressionService:
    """Service for decompressing applicant data and rebuilding detailed records"""
    
    def __init__(self):
        self.repository = ApplicantRepository()
    
    def decompress_applicant(self, applicant_id: str) -> Dict[str, Any]:
        """Decompress applicant data and rebuild detailed Airtable records"""
        logger.info(f"Decompressing applicant: {applicant_id}")
        
        # Get compressed applicant data
        applicant_record = self.repository.get_compressed_applicant(applicant_id)
        if not applicant_record:
            raise ValueError(f"No applicant found with ID {applicant_id}")
        
        fields = applicant_record["fields"]
        compressed_json = fields.get("Compressed JSON")
        if not compressed_json:
            raise ValueError("Compressed JSON field is empty.")
        
        data = json.loads(compressed_json)
        
        personal_data = data.get("personal", {})
        experience_data = data.get("experience", [])
        salary_data = data.get("salary", {})
        
        # Step 1: Save Personal Details
        personal_info = PersonalInfo(
            name=personal_data.get("name"),
            email=personal_data.get("email"),
            location=personal_data.get("location"),
            linkedin=personal_data.get("linkedin")
        )
        personal_record = self.repository.save_personal_info(applicant_id, personal_info)
        personal_id = personal_record["id"]
        
        # Step 2: Save Work Experience
        work_experience_list = [
            WorkExperience(
                company=exp.get("company"),
                title=exp.get("title"),
                start=exp.get("start"),
                end=exp.get("end"),
                technologies=exp.get("technologies")
            )
            for exp in experience_data
        ]
        self.repository.save_work_experience(personal_id, work_experience_list)
        
        # Step 3: Save Salary Preferences
        salary_preferences = SalaryPreferences(
            preferred_rate=salary_data.get("preferred_rate"),
            minimum_rate=salary_data.get("minimum_rate"),
            currency=salary_data.get("currency"),
            availability=salary_data.get("availability")
        )
        self.repository.save_salary_preferences(personal_id, salary_preferences)
        
        logger.info(f"Successfully decompressed and updated Airtable for Applicant ID: {applicant_id}")
        
        return {
            "applicant_id": applicant_id,
            "personal_id": personal_id,
            "personal": personal_info,
            "experience": work_experience_list,
            "salary": salary_preferences
        }
