"""DAO-level exceptions."""


class DaoError(Exception):
    """Base class for DAO exceptions."""

    pass


class DuplicateRecordError(DaoError):
    """Raise if primary key conflict or unique constraint violation occurs."""

    pass


class InvalidOperationError(DaoError):
    """Raise if requested operation failed for business logic reasons."""

    pass


class RecordNotFoundError(DaoError):
    """Raise if requested operation cannot be performed because specified record does not exist."""

    pass
