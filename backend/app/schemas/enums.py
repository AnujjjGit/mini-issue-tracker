from enum import Enum


class Status(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


OPEN_STATUSES = [Status.TODO.value, Status.IN_PROGRESS.value]
COMPLETED_STATUSES = [Status.DONE.value]
