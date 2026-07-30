from __future__ import annotations

DEFAULT_REVIEW_FINDING_CONFIDENCE = 0.8
DEFAULT_REVIEW_ISSUE_SEVERITY = "info"
REVIEW_ISSUE_SEVERITY_RANK = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1,
}
REVIEW_ISSUE_SEVERITY_RANK_DEFAULT = 0
REVIEW_ISSUE_ID_WIDTH = 3
