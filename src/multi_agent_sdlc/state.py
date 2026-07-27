from typing import NotRequired
from typing import Optional, TypedDict
from .models import DevelopmentPlan


class DevState(TypedDict):
    request: str
    plan: Optional[DevelopmentPlan]
    project_directory: NotRequired[str]
