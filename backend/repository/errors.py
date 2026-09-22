class NotFoundError(Exception):
    """Raised by a repository when a referenced row does not exist."""


class ConflictError(Exception):
    """Raised by a repository when an operation violates a DB constraint."""
