"""Encapsulation of bookmark status allowed values and transitions.

Does not really belong in dao layer, but does not belong in api layer either. If a middle layer
arises, move this class there.
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
    def assert_valid_status(cls, status: str):
        """Raise if provided status string is not valid."""
        if status not in cls.VALID_STATUSES:
            raise ValueError("Invalid bookmark status '{0}'; must be one of {1}".format(
                    status, ', '.join(["'{}'".format(s) for s in cls.VALID_STATUSES])))

    @classmethod
    def assert_valid_original_status(cls, status: str):
        """Raise if provided status string may not be set on a newly created bookmark."""
        if status not in cls.VALID_ORIGINAL_STATUSES:
            raise ValueError("Invalid bookmark status for new bookmark '{0}'; must be {1}".format(
                    status, ' or '.join(["'{}'".format(s) for s in cls.VALID_ORIGINAL_STATUSES])))

    @classmethod
    def assert_valid_status_transition(cls, old_status: str, new_status: str):
        """Raise if either status is invalid or if transition from old_status to new_status is not allowed.
        """
        for status in (old_status, new_status):
            cls.assert_valid_status(status)

        # Status can never transition to NEW.
        # All other transitions are valid, at least for now.
        if not (old_status == cls.NEW or new_status != cls.NEW):
            raise ValueError("Invalid bookmark status transition '{0}' -> '{1}'".format(old_status, new_status))

