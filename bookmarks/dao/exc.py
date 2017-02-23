"""DAO-level exceptions."""


class AnansiDaoError(Exception):
    """Base class for DAO exceptions."""

    pass


class DuplicateRecordError(AnansiDaoError):
    """Raise if primary key conflict or unique constraint violation occurs."""

    pass


class InvalidOperationError(AnansiDaoError):
    """Raise if requested operation failed for business logic reasons."""

    pass


class RecordNotFoundError(AnansiDaoError):
    """Raise if requested operation cannot be performed because specified record does not exist."""

    pass
