from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PersonalInfo:
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None


@dataclass
class WorkExperience:
    company: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    technologies: Optional[str] = None


@dataclass
class SalaryPreferences:
    preferred_rate: Optional[int] = None
    minimum_rate: Optional[int] = None
    currency: Optional[str] = None
    availability: Optional[int] = None


@dataclass
class Applicant:
    personal: PersonalInfo
    experience: List[WorkExperience]
    salary: SalaryPreferences
