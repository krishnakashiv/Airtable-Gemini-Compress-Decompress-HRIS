from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScreeningResult:
    is_shortlisted: bool
    reason: str
    score: Optional[int] = None
    summary: Optional[str] = None
    issues: Optional[str] = None
    follow_ups: Optional[str] = None
