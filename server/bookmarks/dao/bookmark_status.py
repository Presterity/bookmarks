"""Encapsulation of bookmark status allowed values and transitions.
"""

__all__ = ('BookmarkStatus',)


class BookmarkStatus(object):
    __doc__ = __doc__

    NEW = 'new'
    SUBMITTED = 'submitted'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    VALID_ORIGINAL_STATUSES = (NEW, SUBMITTED)
    VALID_STATUSES = (NEW, SUBMITTED, ACCEPTED, REJECTED)

    @classmethod
    def is_valid_status(cls, status: str) -> bool:
        """Determine if provided status string is valid."""
        return status in cls.VALID_STATUSES

    @classmethod
    def is_valid_original_status(cls, status: str) -> bool:
        """Determine if provided status string may be set on a newly created bookmark."""
        return status in cls.VALID_ORIGINAL_STATUSES

    @classmethod
    def is_valid_status_transition(cls, old_status: str, new_status: str) -> bool:
        """Determine if transition from old_status to new_status is valid.

        :raise: ValueError if new_status is not valid status
        """
        for status in (old_status, new_status):
            if not cls.is_valid_status(status):
                raise ValueError("Specified status '{0}' is not valid status".format(status))

        # Status can never transition to NEW.
        # All other transitions are valid, at least for now.
        return old_status == cls.NEW or new_status != cls.NEW

