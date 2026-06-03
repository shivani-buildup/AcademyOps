class LeadError(Exception):
    """Base exception for all Lead-related errors."""
    pass

class LeadNotFound(LeadError):
    """Raised when a requested lead is not found in the repository."""
    pass

class DuplicatePhoneError(LeadError):
    """Raised when attempting to create a lead with an existing phone number."""
    pass

class InvalidStageError(LeadError):
    """Raised when an invalid stage transition is attempted."""
    pass
