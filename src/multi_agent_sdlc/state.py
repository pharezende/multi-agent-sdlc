from typing import Optional, TypedDict
from .models import DevelopmentPlan


class DevState(TypedDict):
    request: str  # original user request
    plan: Optional[DevelopmentPlan]
