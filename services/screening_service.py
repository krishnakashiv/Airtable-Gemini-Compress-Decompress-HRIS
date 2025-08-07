from typing import Tuple
from models.applicant import Applicant
from config.business_rules import (
    TIER_1_COMPANIES, 
    MAX_RATE, 
    TOTAL_YEARS_EXPERIENCE, 
    MIN_AVAILABILITY, 
    COUNTRIES,
    calculate_total_experience,
    worked_at_tier1
)


class ScreeningService:
    """Service for screening applicants based on business rules"""
    
    @staticmethod
    def get_shortlist_status(applicant: Applicant) -> Tuple[bool, str]:
        """Determine if applicant should be shortlisted based on business rules"""
        reasons = []
        
        # Convert applicant data to the format expected by the business rules functions
        experience_data = [
            {
                "company": exp.company,
                "title": exp.title,
                "start": exp.start,
                "end": exp.end,
                "technologies": exp.technologies
            }
            for exp in applicant.experience
        ]
        
        salary_data = {
            "preferred_rate": applicant.salary.preferred_rate,
            "minimum_rate": applicant.salary.minimum_rate,
            "currency": applicant.salary.currency,
            "availability": applicant.salary.availability
        }
        
        # Experience
        total_years = calculate_total_experience(experience_data)
        has_tier1 = worked_at_tier1(experience_data)
        experience_ok = total_years >= TOTAL_YEARS_EXPERIENCE or has_tier1
        if experience_ok:
            reasons.append(f"Experience: {round(total_years, 1)} years or Tier-1 company")
        else:
            reasons.append(f"Experience: Only {round(total_years, 1)} years and no Tier-1 company")
        
        # Compensation
        rate = applicant.salary.preferred_rate or 999
        avail = applicant.salary.availability or 0
        compensation_ok = rate <= MAX_RATE and avail >= MIN_AVAILABILITY
        if compensation_ok:
            reasons.append(f"Compensation: ${rate}/hr, {avail} hrs/week")
        else:
            reasons.append(f"Compensation: ${rate}/hr, {avail} hrs/week")
        
        # Location
        location = applicant.personal.location or ""
        location_ok = location in COUNTRIES
        if location_ok:
            reasons.append(f"Location: {location}")
        else:
            reasons.append(f"Location: {location}")
        
        # Final decision
        is_shortlisted = experience_ok and compensation_ok and location_ok
        final_reason = "\n".join(reasons)
        
        return is_shortlisted, final_reason
