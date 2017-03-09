"""Tests for Bookmark DAO objects.

python -m unittest -v bookmarks.dao.test_bookmark_dao
"""

from datetime import datetime, timedelta
import pytz
import unittest
import uuid

from .session import Session
from .test_dao_factory import TestDaoFactory
from .bookmark_dao import Bookmark, BookmarkTopic, BookmarkNote


class BookmarkDaoTestCase(unittest.TestCase):

    def setUp(self):
        self.session = Session.get()
        self._test_bookmark_ids = []

        self._bookmark_id = uuid.uuid4()
        self._url = "http://nytimes.com/news/article.html"
        self._summary = "Good article about peanuts"
        self._sort_date = datetime(2017, 2, 7, 18, 30, tzinfo=pytz.utc)

    def tearDown(self):
        # Delete test bookmarks
        for bookmark_id in self._test_bookmark_ids:
            self.session.query(Bookmark).filter_by(bookmark_id=bookmark_id).delete()
        Session.close()

    def _create_test_bookmark(self):
        """Return Bookmark that has been saved to db."""
        self._save_bookmark(Bookmark(bookmark_id=self._bookmark_id,
                                     url=self._url,
                                     summary=self._summary,
                                     sort_date=self._sort_date))
        return self._select_bookmark(self._bookmark_id)

    def _save_bookmark(self, bookmark):
        """Helper function for saving bookmark to database; records id for cleanup"""
        saved_bookmark = self.session.merge(bookmark)
        self.session.flush()
        self._test_bookmark_ids.append(saved_bookmark.bookmark_id)
        return saved_bookmark

    def _select_bookmarks(self):
        """Select all bookmarks."""
        return self.session.query(Bookmark).all()

    def _select_bookmark(self, bookmark_id):
        """Retrieve specified bookmark from db; return None if it is not found."""
        return self.session.query(Bookmark).filter_by(bookmark_id=bookmark_id).first()
        

class BookmarkTests(BookmarkDaoTestCase):
    """Verify Bookmark ORM."""

    def setUp(self):
        super(BookmarkTests, self).setUp()

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
            sort_date=self._sort_date)

        saved_bookmark = self._save_bookmark(bookmark)

        bookmarks = self._select_bookmarks()
        self.assertEqual(1, len(bookmarks))
        retrieved_bookmark = bookmarks[0]

        # Verify specified attributes
        self.assertIsNotNone(retrieved_bookmark.bookmark_id)
        self.assertTrue(isinstance(retrieved_bookmark.bookmark_id, uuid.UUID))
        self.assertEqual(self._url, retrieved_bookmark.url)
        self.assertEqual(self._summary, retrieved_bookmark.summary)
        self.assertEqual(self._sort_date, retrieved_bookmark.sort_date)

        # Verify default attributes
        self.assertEqual('new', retrieved_bookmark.status)
        self.assertEqual('%Y.%m.%d', retrieved_bookmark.display_date_format)

        # Verify NULLABLE attributes
        for attr in ('source', 'source_item_id', 'submitter_id', 'submission_date'):
            self.assertIsNone(getattr(retrieved_bookmark, attr))

        q = self.session.query(Bookmark)
        q = q.order_by(Bookmark.sort_date)
        foo = q.all()
        self.assertEqual(1, len(foo))

    def test_bookmark__all(self):
        """Verify Bookmark creation with all data specified."""
        bookmark = Bookmark(
            bookmark_id=self._bookmark_id,
            url=self._url,
            summary=self._summary,
            sort_date=self._sort_date,
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
        self.assertEqual(self._bookmark_id, retrieved_bookmark.bookmark_id)
        self.assertEqual(self._description, retrieved_bookmark.description)
        self.assertEqual(self._display_date_format, retrieved_bookmark.display_date_format)
        self.assertEqual(self._status, retrieved_bookmark.status)
        self.assertEqual(self._source, retrieved_bookmark.source)
        self.assertEqual(self._source_item_id, retrieved_bookmark.source_item_id)
        self.assertEqual(self._source_last_updated, retrieved_bookmark.source_last_updated)
        self.assertEqual(self._submitter_id, retrieved_bookmark.submitter_id)
        self.assertEqual(self._submission_date, retrieved_bookmark.submission_date)

    def test_bookmark__specify_bookmark_id(self):
        """Verify Bookmark creation with specified bookmark_id."""
        bookmark = Bookmark(
            bookmark_id=self._bookmark_id,
            url=self._url,
            summary=self._summary,
            sort_date=self._sort_date)
        self._save_bookmark(bookmark)

        bookmarks = self.session.query(Bookmark).all()
        self.assertEqual(1, len(bookmarks))
        retrieved_bookmark = bookmarks[0]
        self.assertEqual(self._bookmark_id, retrieved_bookmark.bookmark_id)


class BookmarkMethodTests(BookmarkDaoTestCase):
    """Verify behavior of convenience CRUD methods.

    Since Bookmark itself is verified in other tests, this test will use TestDaoFactory
    for convenience.
    """

    def test_select_bookmarks__no_bookmarks(self):
        """Verify empty list returned by Bookmark.select_bookmarks when there are none.
        """
        self.assertEqual(([], None), Bookmark.select_bookmarks())

    def test_select_bookmarks(self):
        """Verify Bookmark.select_bookmarks result."""
        today = datetime.utcnow().replace(tzinfo=pytz.utc)
        today_bookmark = TestDaoFactory.create_bookmark(sort_date=today)
        yesterday_bookmark = TestDaoFactory.create_bookmark(sort_date=today - timedelta(days=1))
        saved_bookmarks = [self._save_bookmark(b) for b in [today_bookmark, yesterday_bookmark]]
        self.session.flush()
        self.session.commit()

        # Verify expected ids in expected order (ascending by date)
        selected_bookmarks, cursor = Bookmark.select_bookmarks()
        self.assertEqual([yesterday_bookmark.bookmark_id, today_bookmark.bookmark_id],
                         [b.bookmark_id for b in selected_bookmarks])
        self.assertTrue(isinstance(cursor, str))

    def test_select_bookmarks_by_topic(self):
        """Verify Bookmark.select_bookmarks result when topic is specified."""
        topic = "Hello World"
        topic_bookmark = TestDaoFactory.create_bookmark(
            topics=[TestDaoFactory.create_bookmark_topic(topic=topic)])
        other_topic_bookmark = TestDaoFactory.create_bookmark(
            topics=[TestDaoFactory.create_bookmark_topic(topic="Aloha World")])
        no_topic_bookmark = TestDaoFactory.create_bookmark()
        saved_bookmarks = [self._save_bookmark(b) for b in 
                           [other_topic_bookmark, topic_bookmark, no_topic_bookmark]]
        self.session.flush()
        self.session.commit()

        # Verify selection
        selected_bookmarks, cursor = Bookmark.select_bookmarks(topics=[topic])
        self.assertEqual([topic_bookmark.bookmark_id], [b.bookmark_id for b in selected_bookmarks])
        self.assertTrue(isinstance(cursor, str))

    def test_select_bookmarks_by_topic__no_matching_bookmarks(self):
        """Verify Bookmark.select_bookmarks result when topic does not match any bookmarks."""
        topic = "Hello World"
        other_topic_bookmark = TestDaoFactory.create_bookmark(
            topics=[TestDaoFactory.create_bookmark_topic(topic="Aloha World")])
        no_topic_bookmark = TestDaoFactory.create_bookmark()
        saved_bookmarks = [self._save_bookmark(b) for b in 
                           [other_topic_bookmark, no_topic_bookmark]]
        self.session.flush()
        self.session.commit()

        # Verify selection
        self.assertEqual(([], None), Bookmark.select_bookmarks(topics=[topic]))

    def test_select_bookmarks_by_topic__multiple_topics(self):
        """Verify Bookmark.select_bookmarks result when multiple topics are specified."""
        topics = ["Hello World", "Aloha World"]
        topic_zero_bookmark = TestDaoFactory.create_bookmark(
            topics=[TestDaoFactory.create_bookmark_topic(topic=topics[0])])
        topic_one_bookmark = TestDaoFactory.create_bookmark(
            topics=[TestDaoFactory.create_bookmark_topic(topic=topics[1])])
        other_topic_bookmark = TestDaoFactory.create_bookmark(
            topics=[TestDaoFactory.create_bookmark_topic(topic="Banana Bread")])
        saved_bookmarks = [self._save_bookmark(b) for b in 
                           [other_topic_bookmark, topic_zero_bookmark, topic_one_bookmark]]
        self.session.flush()
        self.session.commit()

        # Verify selection: Should be OR of bookmarks with any specified topic
        selected_bookmarks, cursor = Bookmark.select_bookmarks(topics=topics)
        self.assertEqual(set([topic_zero_bookmark.bookmark_id, topic_one_bookmark.bookmark_id]), 
                         set([b.bookmark_id for b in selected_bookmarks]))
        self.assertTrue(isinstance(cursor, str))

    def test_select_bookmarks_by_topic__multiple_topics__double_match(self):
        """Verify Bookmark.select_bookmarks result dedupes double topic match."""
        topics = ["Hello World", "Aloha World"]
        double_match_bookmark = TestDaoFactory.create_bookmark(
            topics=[TestDaoFactory.create_bookmark_topic(topic=t) for t in topics])
        saved_bookmarks = [self._save_bookmark(double_match_bookmark)]
        self.session.flush()
        self.session.commit()

        # Verify selection: Should be length 1
        selected_bookmarks, cursor = Bookmark.select_bookmarks(topics=topics)
        self.assertEqual([double_match_bookmark.bookmark_id], [b.bookmark_id for b in selected_bookmarks])
        self.assertTrue(isinstance(cursor, str))

    def test_select_bookmarks__cursor(self):
        """Verify cursor functionality of select_bookmarks."""
        today = datetime.utcnow().replace(tzinfo=pytz.utc, microsecond=0)
        today_bookmark = TestDaoFactory.create_bookmark(sort_date=today)
        yesterday_bookmark_ids = sorted([uuid.uuid4(), uuid.uuid4()])
        yesterday_bookmark_1 = TestDaoFactory.create_bookmark(sort_date=(today-timedelta(days=1)), bookmark_id=yesterday_bookmark_ids[0])
        yesterday_bookmark_2 = TestDaoFactory.create_bookmark(sort_date=(today-timedelta(days=1)), bookmark_id=yesterday_bookmark_ids[1])
        two_days_ago_bookmark = TestDaoFactory.create_bookmark(sort_date=today-timedelta(days=2))
        saved_bookmarks = [self._save_bookmark(b) for b in [today_bookmark, two_days_ago_bookmark, yesterday_bookmark_2, yesterday_bookmark_1]]
        self.session.flush()
        self.session.commit()

        # Expected return order: 
        #  two_days_ago_bookmark
        #  yesterday_bookmark_1
        #  yesterday_bookmark_2
        #  today_bookmark
        
        # Select first two records
        selected_bookmarks, cursor = Bookmark.select_bookmarks(max_results=2)
        self.assertEqual([two_days_ago_bookmark.bookmark_id, yesterday_bookmark_1.bookmark_id],
                         [b.bookmark_id for b in selected_bookmarks])
        self.assertIsNotNone(cursor)

        # Select next one record
        selected_bookmarks, cursor = Bookmark.select_bookmarks(cursor=cursor, max_results=1)
        self.assertEqual([yesterday_bookmark_2.bookmark_id], [b.bookmark_id for b in selected_bookmarks])
        self.assertIsNotNone(cursor)

        # Select last record
        selected_bookmarks, cursor = Bookmark.select_bookmarks(cursor=cursor)
        self.assertEqual([today_bookmark.bookmark_id], [b.bookmark_id for b in selected_bookmarks])
        self.assertIsNotNone(cursor)

    def test_select_bookmark_by_id(self):
        """Verify Bookmark.select_bookmark_by_id."""
        match_bookmark = TestDaoFactory.create_bookmark()
        other_bookmark = TestDaoFactory.create_bookmark()
        saved_bookmarks = [self._save_bookmark(b) for b in [other_bookmark, match_bookmark]]
        self.session.flush()
        self.session.commit()

        # Verify selection
        selected_bookmark = Bookmark.select_bookmark_by_id(match_bookmark.bookmark_id)
        self.assertEqual(match_bookmark.bookmark_id, selected_bookmark.bookmark_id)

    def test_select_bookmark_by_id__no_bookmark(self):
        """Verify Bookmark.select_bookmark_by_id when on such bookmark exists."""
        bookmark = TestDaoFactory.create_bookmark()
        other_bookmark = TestDaoFactory.create_bookmark()
        saved_bookmarks = [self._save_bookmark(b) for b in [other_bookmark, bookmark]]
        self.session.flush()
        self.session.commit()

        # Verify selection
        self.assertIsNone(Bookmark.select_bookmark_by_id(uuid.uuid4()))


class BookmarkTopicTests(BookmarkDaoTestCase):
    """Verify BookmarkTopic ORM."""

    def setUp(self):
        super(BookmarkTopicTests, self).setUp()
        self._topic = 'Test Topic'
        self._created_on = datetime.utcnow().replace(tzinfo=pytz.utc)

    def _select_bookmark_topics(self, bookmark_id):
        """Retrieve specified bookmark topics from db; return empty list if None exist."""
        return self.session.query(BookmarkTopic).filter_by(bookmark_id=bookmark_id).all()

    def test_bookmark_topic(self):
        """Verify BookmarkTopic creation."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        bookmark_topic = BookmarkTopic(bookmark_id=self._bookmark_id,
                                       topic=self._topic,
                                       created_on=self._created_on)
        self.session.merge(bookmark_topic)
        self.session.flush()
        
        topics = self._select_bookmark_topics(self._bookmark_id)
        self.assertEqual(1, len(topics))
        self.assertEqual(self._topic, topics[0].topic)
        self.assertEqual(self._created_on, topics[0].created_on)

    def test_bookmark_topic__delete_leaves_bookmark(self):
        """Verify BookmarkTopic deletion leaves parent Bookmark intact."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        bookmark_topic = BookmarkTopic(bookmark_id=self._bookmark_id,
                                       topic=self._topic,
                                       created_on=self._created_on)
        self.session.merge(bookmark_topic)
        self.session.flush()

        self.session.query(BookmarkTopic).filter_by(bookmark_id=self._bookmark_id).delete()
        self.session.flush()
        self.assertEqual([], self._select_bookmark_topics(self._bookmark_id))
        self.assertIsNotNone(self._select_bookmark(self._bookmark_id))

    def test_bookmark_relation__retrieval(self):
        """Verify that retrieving bookmark retrieves topics."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        bookmark_topic = BookmarkTopic(bookmark_id=self._bookmark_id,
                                       topic=self._topic,
                                       created_on=self._created_on)
        self.session.merge(bookmark_topic)
        self.session.flush()
        
        bookmark = self._select_bookmark(self._bookmark_id)
        self.assertEqual(1, len(bookmark.topics))
        self.assertEqual(self._topic, bookmark.topics[0].topic)

    def test_bookmark_relation__save(self):
        # Create and save bookmark first because of FK relationship
        bookmark_topic = BookmarkTopic(topic=self._topic,
                                       created_on=self._created_on)
        bookmark = Bookmark(
            url=self._url,
            summary=self._summary,
            sort_date=self._sort_date,
            topics=[bookmark_topic])

        saved_bookmark = self._save_bookmark(bookmark)
        self.session.flush()

        bookmark = self._select_bookmark(saved_bookmark.bookmark_id)
        self.assertIsNotNone(bookmark)
        self.assertEqual(1, len(bookmark.topics))
        self.assertEqual(self._topic, bookmark.topics[0].topic)


class BookmarkNoteTests(BookmarkDaoTestCase):
    """Verify BookmarkNote ORM."""

    def setUp(self):
        super(BookmarkNoteTests, self).setUp()
        self._node_id = uuid.uuid4()
        self._text = 'It was a dark and stormy night'
        self._author = 'me, myself and i'
        self._created_on = datetime.utcnow().replace(tzinfo=pytz.utc)

    def _select_bookmark_notes(self, bookmark_id):
        """Retrieve specified bookmark notes from db; return empty list if None exist."""
        return self.session.query(BookmarkNote).filter_by(bookmark_id=bookmark_id).all()

    def test_bookmark_note(self):
        """Verify BookmarkNote creation; verify that note_id is assigned."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        bookmark_note = BookmarkNote(bookmark_id=self._bookmark_id,
                                     text=self._text,
                                     author=self._author,
                                     created_on=self._created_on)
        self.session.merge(bookmark_note)
        self.session.flush()
        
        notes = self._select_bookmark_notes(self._bookmark_id)
        self.assertEqual(1, len(notes))
        self.assertIsNotNone(notes[0].note_id)
        self.assertTrue(isinstance(notes[0].note_id, uuid.UUID))
        self.assertEqual(self._bookmark_id, notes[0].bookmark_id)
        self.assertEqual(self._text, notes[0].text)
        self.assertEqual(self._author, notes[0].author)
        self.assertEqual(self._created_on, notes[0].created_on)

    def test_bookmark_note__specify_note_id(self):
        """Verify BookmarkNote creation with specified note_id."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        note_id = uuid.uuid4()
        bookmark_note = BookmarkNote(note_id=note_id,
                                     bookmark_id=self._bookmark_id,
                                     text=self._text,
                                     author=self._author,
                                     created_on=self._created_on)
        self.session.merge(bookmark_note)
        self.session.flush()
        
        notes = self._select_bookmark_notes(self._bookmark_id)
        self.assertEqual(1, len(notes))
        self.assertEqual(note_id, notes[0].note_id)

    def test_bookmark_note__delete_leaves_bookmark(self):
        """Verify BookmarkNote deletion leaves parent Bookmark intact."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        bookmark_note = BookmarkNote(bookmark_id=self._bookmark_id,
                                     text=self._text,
                                     author=self._author,
                                     created_on=self._created_on)
        self.session.merge(bookmark_note)
        self.session.flush()

        self.session.query(BookmarkNote).filter_by(bookmark_id=self._bookmark_id).delete()
        self.session.flush()
        self.assertEqual([], self._select_bookmark_notes(self._bookmark_id))
        self.assertIsNotNone(self._select_bookmark(self._bookmark_id))

    def test_bookmark_relation__retrieval(self):
        """Verify that retrieving bookmark retrieves notes."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        bookmark_note = BookmarkNote(bookmark_id=self._bookmark_id,
                                     text=self._text,
                                     author=self._author,
                                     created_on=self._created_on)
        self.session.merge(bookmark_note)
        self.session.flush()
        
        bookmark = self._select_bookmark(self._bookmark_id)
        self.assertEqual(1, len(bookmark.notes))
        self.assertEqual(self._text, bookmark.notes[0].text)

    def test_bookmark_relation__save(self):
        """Verify that bookmark note is saved along with bookmark."""
        bookmark_note = BookmarkNote(text=self._text,
                                     author=self._author,
                                     created_on=self._created_on)
        bookmark = Bookmark(
            url=self._url,
            summary=self._summary,
            sort_date=self._sort_date,
            notes=[bookmark_note])

        saved_bookmark = self._save_bookmark(bookmark)
        self.session.flush()

        bookmark = self._select_bookmark(saved_bookmark.bookmark_id)
        self.assertIsNotNone(bookmark)
        self.assertEqual(1, len(bookmark.notes))
        self.assertTrue(isinstance(bookmark.notes[0].note_id, uuid.UUID))
        self.assertEqual(self._text, bookmark.notes[0].text)

    
        

        
