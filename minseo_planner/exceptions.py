

class PlannerError(Exception):
    """Base class for planner exceptions."""
    pass

class DataFileError(PlannerError):
    """Raised when data files are missing or corrupt."""
    pass

class ValidationError(PlannerError):
    """Raised for invalid user input or time formats."""
    pass
