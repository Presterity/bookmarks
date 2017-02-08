"""Tests for Bookmark DAO objects.
"""

from datetime import datetime
import pytz
import unittest
import uuid

from .core import get_session
from .bookmark_dao import Bookmark, BookmarkTopic, BookmarkNote


class BookmarkDaoTestCase(unittest.TestCase):
    def setUp(self):
        self.session = get_session()
        self._bookmark_ids = []

    def tearDown(self):
        # Delete test bookmarks
        for bookmark_id in self._bookmark_ids:
            self.session.query(Bookmark).filter_by(bookmark_id=bookmark_id).delete()
        self.session.flush()

    def _save_bookmark(self, bookmark):
        saved_bookmark = self.session.merge(bookmark)
        self.session.flush()
        self._bookmark_ids.append(saved_bookmark.bookmark_id)
        

class BookmarkTests(BookmarkDaoTestCase):
    """Verify Bookmark ORM."""

    def setUp(self):
        super(BookmarkTests, self).setUp()

        self._uuid = uuid.uuid4()
        self._url = "http://nytimes.com/news/article.html"
        self._summary = "Good article about peanuts"
        self._event_date = datetime(2017, 2, 7, 18, 30, tzinfo=pytz.utc)
        self._description = "Peanuts do not grow on trees!"
        self._display_date_format = '%Y.%m'
        self._status = 'duplicate'
        self._source = 'raindrop'
        self._source_item_id = '1234-abc'
        self._source_last_updated = datetime(2017, 2, 7, 23, 10, tzinfo=pytz.utc)
        self._submitter_id = 'aladdin'
        self._submission_date = datetime.utcnow().replace(tzinfo=pytz.utc)

    def test_bookmark__required(self):
        """Verify Bookmark creation with only required data."""
        bookmark = Bookmark(
            url=self._url,
            summary=self._summary,
            event_date=self._event_date)
        self._save_bookmark(bookmark)

        bookmarks = self.session.query(Bookmark).all()
        self.assertEqual(1, len(bookmarks))
        retrieved_bookmark = bookmarks[0]

        # Verify specified attributes
        self.assertIsNotNone(retrieved_bookmark.bookmark_id)
        self.assertEqual(self._url, retrieved_bookmark.url)
        self.assertEqual(self._summary, retrieved_bookmark.summary)
        self.assertEqual(self._event_date, retrieved_bookmark.event_date)

        # Verify default attributes
        self.assertEqual('new', retrieved_bookmark.status)
        self.assertEqual('%Y.%m.%d', retrieved_bookmark.display_date_format)

        # Verify NULLABLE attributes
        for attr in ('source', 'source_item_id', 'submitter_id', 'submission_date'):
            self.assertIsNone(getattr(retrieved_bookmark, attr))

    def test_bookmark__all(self):
        """Verify Bookmark creation with all data specified."""
        bookmark = Bookmark(
            bookmark_id=self._uuid,
            url=self._url,
            summary=self._summary,
            event_date=self._event_date,
            description=self._description,
            display_date_format=self._display_date_format,
            status=self._status,
            source=self._source,
            source_item_id=self._source_item_id,
            source_last_updated=self._source_last_updated,
            submitter_id=self._submitter_id,
            submission_date=self._submission_date)
        self._save_bookmark(bookmark)
        bookmarks = self.session.query(Bookmark).all()
        self.assertEqual(1, len(bookmarks))
        retrieved_bookmark = bookmarks[0]

        # Verify newly-specified attributes
        self.assertEqual(self._uuid, retrieved_bookmark.bookmark_id)
        self.assertEqual(self._description, retrieved_bookmark.description)
        self.assertEqual(self._display_date_format, retrieved_bookmark.display_date_format)
        self.assertEqual(self._status, retrieved_bookmark.status)
        self.assertEqual(self._source, retrieved_bookmark.source)
        self.assertEqual(self._source_item_id, retrieved_bookmark.source_item_id)
        self.assertEqual(self._source_last_updated, retrieved_bookmark.source_last_updated)
        self.assertEqual(self._submitter_id, retrieved_bookmark.submitter_id)
        self.assertEqual(self._submission_date, retrieved_bookmark.submission_date)


class BookmarkTopicTests(BookmarkDaoTestCase):
    """Verify BookmarkTopic ORM."""
    def test_bookmark_topic(self):
        """Verify BookmarkTopic creation."""
        bookmark_topic = BookmarkTopic()

        
class BookmarkNoteTests(BookmarkDaoTestCase):
    """Verify BookmarkNote ORM."""
    def test_bookmark_note(self):
        """Verify BookmarkNote creation."""
        bookmark_note = BookmarkNote()


