class DomainError(Exception):
    """Base exception for all domain errors."""
    pass

class InvalidEmail(DomainError):
    """Raised when an email is invalid."""
    pass

class InvalidQuestionOptions(DomainError):
    """Raised when question options are invalid (e.g. less than 2, or no correct option)."""
    pass

class InvalidTriviaComposition(DomainError):
    """Raised when trivia composition is invalid (e.g. empty name, duplicate ids)."""
    pass

class ParticipationFinished(DomainError):
    """Raised when trying to perform an action on a finished participation."""
    pass

class InvalidScore(DomainError):
    """Raised when a score is invalid."""
    pass
