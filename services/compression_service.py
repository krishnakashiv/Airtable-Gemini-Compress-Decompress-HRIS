import json
from typing import Dict, Any
from data_access.applicant_repository import ApplicantRepository
from services.screening_service import ScreeningService
from services.llm_service import analyze_applicant
from models.applicant import Applicant


class CompressionService:
    """Service for compressing applicant data and performing analysis"""
    
    def __init__(self):
        self.repository = ApplicantRepository()
    
    def compress_applicant(self, applicant_id: str) -> Dict[str, Any]:
        """Compress applicant data into a single JSON structure"""
        # Get applicant data
        applicant = self.repository.get_applicant(applicant_id)
        if not applicant:
            raise ValueError(f"No applicant found with ID {applicant_id}")
        
        # Build compressed JSON
        compressed = {
            "personal": {
                "name": applicant.personal.name,
                "email": applicant.personal.email,
                "location": applicant.personal.location,
                "linkedin": applicant.personal.linkedin
            },
            "experience": [
                {
                    "company": exp.company,
                    "title": exp.title,
                    "start": exp.start,
                    "end": exp.end,
                    "technologies": exp.technologies
                }
                for exp in applicant.experience
            ],
            "salary": {
                "preferred_rate": applicant.salary.preferred_rate,
                "minimum_rate": applicant.salary.minimum_rate,
                "currency": applicant.salary.currency,
                "availability": applicant.salary.availability
            }
        }
        
        # Perform screening
        is_shortlisted, reason = ScreeningService.get_shortlist_status(applicant)
        shortlist_status = "Shortlisted" if is_shortlisted else "Rejected"
        
        # LLM Analysis
        llm_result = analyze_applicant(compressed)
        
        llm_score = llm_result.get("score", None)
        llm_summary = llm_result.get("summary", None)
        llm_issues = llm_result.get("issues", None)
        llm_follow_ups = llm_result.get("follow_ups", None)
        
        # Format follow-ups
        if llm_follow_ups:
            formatted_followups = "\n".join([f"• {line}" for line in llm_follow_ups.splitlines()])
        else:
            formatted_followups = None
        
        # Save to Airtable
        compressed_json_str = json.dumps(compressed, indent=2)
        applicant_record = self.repository.save_compressed_applicant(
            applicant_id, 
            compressed_json_str, 
            shortlist_status, 
            llm_score, 
            llm_summary, 
            formatted_followups
        )
        
        # Add to shortlisted leads if qualified
        if is_shortlisted:
            self.repository.save_shortlisted_lead(
                applicant_record["id"], 
                compressed_json_str, 
                reason
            )
        
        return {
            "applicant_id": applicant_id,
            "compressed_data": compressed,
            "shortlist_status": shortlist_status,
            "llm_score": llm_score,
            "llm_summary": llm_summary,
            "llm_issues": llm_issues,
            "llm_follow_ups": formatted_followups,
            "reason": reason
        }
