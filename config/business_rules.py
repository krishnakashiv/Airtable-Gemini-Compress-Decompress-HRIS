from datetime import datetime
import logging

# Business rules configuration

logger = logging.getLogger(__name__)

TIER_1_COMPANIES = set(["google", "meta", "openai"])
MAX_RATE = 100
TOTAL_YEARS_EXPERIENCE = 4
MIN_AVAILABILITY = 20
COUNTRIES = set(["USA", "Canada", "UK", "Germany", "India"])


def calculate_total_experience(experience_list):
    total_days = 0
    for exp in experience_list:
        try:
            start = datetime.strptime(exp["start"], "%Y-%m-%d")
            end = datetime.strptime(exp["end"], "%Y-%m-%d")
            total_days += (end - start).days
        except Exception as e:
            logger.warning(f"Error parsing dates: {e}")
            continue
    return total_days / 365  # convert to years


def worked_at_tier1(experience_list):
    companies = set()
    for exp in experience_list:
        companies.add(exp.get("company", "").lower())
    
    if companies.intersection(TIER_1_COMPANIES):
        return True
    return False
