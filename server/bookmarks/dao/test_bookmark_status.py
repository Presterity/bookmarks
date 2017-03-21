"""Tests for BookmarkStatus.

python -m unittest -v bookmarks.dao.test_bookmark_status
"""

import unittest

from .bookmark_dao import BookmarkStatus


class BookmarkStatusTests(unittest.TestCase):
    def test_is_valid(self):
        """Verify that all VALID_STATUSES are in fact, valid."""
        for status in BookmarkStatus.VALID_STATUSES:
            self.assertTrue(BookmarkStatus.is_valid_status(status))

    def test_is_valid__case_sensitive(self):
        """Verify that all VALID_STATUSES are invalid if they are uppercased."""
        for status in BookmarkStatus.VALID_STATUSES:
            self.assertFalse(BookmarkStatus.is_valid_status(status.upper()))

    def test_is_valid__invalid(self):
        """Verify that made-up statuses are not valid."""
        for status in ('free', 'to', 'be', 'you', 'and', 'me'):
            self.assertFalse(BookmarkStatus.is_valid_status(status))

    def test_is_valid__None(self):
        """Verify that is_valid_status handles None argument gracefully."""
        self.assertFalse(BookmarkStatus.is_valid_status(None))

    def test_is_valid_original_status(self):
        """Verify that only 'new' and 'submitted' are valid original statuses."""
        for status in BookmarkStatus.VALID_ORIGINAL_STATUSES:
            self.assertTrue(BookmarkStatus.is_valid_original_status(status))

    def test_is_valid_original_status__invalid(self):
        """Verify that other strings, including other valid statuses, are not valid original statuses."""
        for status in set(BookmarkStatus.VALID_STATUSES).difference(set(BookmarkStatus.VALID_ORIGINAL_STATUSES)):
            self.assertFalse(BookmarkStatus.is_valid_original_status(status))
        
        for status in ('every', 'giant', 'bird', 'dives', 'fast'):
            self.assertFalse(BookmarkStatus.is_valid_original_status(status))

    def test_is_valid_status_transition__from_new(self):
        """Verify that any transition out of 'new' is valid."""
        for status in BookmarkStatus.VALID_STATUSES:
            self.assertTrue(BookmarkStatus.is_valid_status_transition(BookmarkStatus.NEW, status))

    def test_is_valid_status_transition__to_new(self):
        """Verify that any transition to 'new' is invalid."""
        for status in BookmarkStatus.VALID_STATUSES:
            if status == BookmarkStatus.NEW:
                continue
            self.assertFalse(BookmarkStatus.is_valid_status_transition(status, BookmarkStatus.NEW))

    def test_is_valid_status_transition__from_submitted(self):
        """Verify that transition from submitted to accepted or rejected is valid."""
        for status in (BookmarkStatus.ACCEPTED, BookmarkStatus.REJECTED):
            self.assertTrue(BookmarkStatus.is_valid_status_transition(BookmarkStatus.SUBMITTED, status))

    def test_is_valid_status_transition__from_rejected(self):
        """Verify that transition from rejected to submitted or accepted is valid."""
        for status in (BookmarkStatus.ACCEPTED, BookmarkStatus.SUBMITTED):
            self.assertTrue(BookmarkStatus.is_valid_status_transition(BookmarkStatus.REJECTED, status))

    def test_is_valid_status_transition__from_accepted(self):
        """Verify that transition from accepted to submitted or rejected is valid."""
        for status in (BookmarkStatus.REJECTED, BookmarkStatus.SUBMITTED):
            self.assertTrue(BookmarkStatus.is_valid_status_transition(BookmarkStatus.ACCEPTED, status))

    def test_is_valid_status_transition__invalid_status(self):
        """Verify that if either status arg is invalid, is_valid_status_transition raises."""
        for old, new in [(BookmarkStatus.ACCEPTED, 'foo'), ('foo', BookmarkStatus.ACCEPTED)]:
            self.assertRaisesRegex(ValueError,
                                   "Specified status 'foo' is not valid status",
                                   BookmarkStatus.is_valid_status_transition,
                                   old, new)
