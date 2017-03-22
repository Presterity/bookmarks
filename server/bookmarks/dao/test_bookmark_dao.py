"""Tests for Bookmark DAO objects.

python -m unittest -v bookmarks.dao.test_bookmark_dao
"""

from datetime import datetime, timedelta
import pytz
import unittest
from unittest.mock import patch, Mock
import uuid

from .session import Session
from .test_dao_factory import TestDaoFactory
from .bookmark_dao import Bookmark, BookmarkTopic, BookmarkNote, BookmarkStatus


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

    def _create_test_bookmark(self, **kwargs):
        """Return Bookmark that has been saved to db."""
        attrs = {'bookmark_id': self._bookmark_id,
                 'url': self._url,
                 'summary': self._summary,
                 'sort_date': self._sort_date}
        attrs.update(**kwargs)
        self._save_bookmark(Bookmark(**attrs))
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
        self._submitted_on = datetime.utcnow().replace(tzinfo=pytz.utc)

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
        for attr in ('source', 'source_item_id', 'submitter_id', 'submitted_on'):
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
            submitted_on=self._submitted_on)
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
        self.assertEqual(self._submitted_on, retrieved_bookmark.submitted_on)

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


class BookmarkCreateTests(BookmarkDaoTestCase):
    """Verify create_bookmark behavior."""

    def setUp(self):
        super(BookmarkCreateTests, self).setUp()
        self._display_date = self._sort_date.strftime("%Y.%m.%d")

    def _create_bookmark(self, **kwargs):
        """Wrapper around Bookmark.create_bookmark that registers bookmark_id for cleanup."""
        bookmark = Bookmark.create_bookmark(**kwargs)
        self._test_bookmark_ids.append(bookmark.bookmark_id)
        return bookmark

    def _select_topics(self):
        """Select all topics."""
        return self.session.query(BookmarkTopic).all()

    @patch.object(Bookmark, '_parse_display_date')
    def test_create_bookmark__simple(self, mock_parse_display_date):
        """Verify bookmark creation with only required args."""
        # Set up mocks and test data
        test_date_format = 'foo'
        mock_parse_display_date.return_value = (self._sort_date, test_date_format)

        # Create bookmark
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._sort_date}
        bookmark = self._create_bookmark(**args)
        
        # Verify result
        self.assertIsNotNone(bookmark)
        self.assertIsNotNone(bookmark.bookmark_id)
        self.assertEqual(self._summary, bookmark.summary)
        self.assertEqual(self._url, bookmark.url)
        self.assertEqual(self._sort_date, bookmark.sort_date)
        self.assertEqual(test_date_format, bookmark.display_date_format)
        self.assertEqual('new', bookmark.status)
        self.assertIsNone(bookmark.description)
        self.assertEqual([], bookmark.topics)
        self.assertIsNotNone(bookmark.created_on)
        self.assertIsNone(bookmark.submitted_on)

        # Verify mocks
        mock_parse_display_date.assert_called_once_with(self._sort_date)

        # Verify bookmark is persisted to database
        self.session.flush()
        self.session.commit()
        self.assertEqual(bookmark, self._select_bookmark(bookmark.bookmark_id))

    def test_create_bookmark__bookmark_id(self):
        """Verify bookmark creation with specified bookmark_id."""
        # Create bookmark
        bookmark_id = uuid.uuid4()
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date,
                'bookmark_id': bookmark_id
                }
        bookmark = self._create_bookmark(**args)
        self.assertEqual(bookmark_id, bookmark.bookmark_id)

    def test_create_bookmark__description(self):
        """Verify Bookmark creation with description."""
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date,
                'description': 'eeny meeny miney mo'
                }
        bookmark = self._create_bookmark(**args)
        self.assertEqual('eeny meeny miney mo', bookmark.description)

    def test_create_bookmark__submitted(self):
        """Verify Bookmark creation with status 'submitted'."""
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date,
                'status': 'submitted'
                }
        bookmark = self._create_bookmark(**args)
        self.assertEqual('submitted', bookmark.status)
        self.assertIsNotNone(bookmark.submitted_on)

    def test_create_bookmark__submitted_ci(self):
        """Verify Bookmark creation with status 'SUBMITTED'."""
        utcnow = datetime.utcnow().replace(microsecond=0)
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date,
                'status': 'SUBMITTED'
                }
        bookmark = self._create_bookmark(**args)
        self.assertEqual('submitted', bookmark.status)
        self.assertTrue(utcnow <= bookmark.submitted_on)

    def test_create_bookmark__topics(self):
        """Verify Bookmark and Topic creation when topics are specified."""
        self.assertEqual([], self._select_topics())
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date,
                'topics': ['ada', 'fortran', 'pascal']
                }
        bookmark = self._create_bookmark(**args)
        self.assertEqual(set(args['topics']), set([t.topic for t in bookmark.topics]))

        # Verify that topics were created
        topics = self._select_topics()
        self.assertEqual(set(args['topics']), set([t.topic for t in topics]))
        for t in topics:
            self.assertEqual(bookmark.bookmark_id, t.bookmark_id)

    def test_create_bookmark__missing_required_arg(self):
        """Verify bookmark creation without required args raises."""

        def get_args():
            return {'summary': self._summary,
                    'url': self._url,
                    'display_date': self._sort_date}
        for required_key in ('summary', 'url', 'display_date'):
            args = get_args()
            del args[required_key]
            self.assertRaisesRegex(ValueError,
                                   "Missing required argument '{0}'".format(required_key),
                                   self._create_bookmark,
                                   **args)
            
    @patch.object(Bookmark, '_parse_display_date')
    def test_create_bookmark__invalid_date_format(self, mock_parse_display_date):
        """Verify create_bookmark raises if date_format is unrecognized."""
        mock_parse_display_date.side_effect = ValueError('bad format')
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date
                }
        self.assertRaisesRegex(ValueError,
                               'bad format',
                               self._create_bookmark,
                               **args)

    def test_create_bookmark__invalid_status(self):
        """Verify create_bookmark raises if status is other than 'new' or 'submitted'."""
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date,
                'status': 'freida'
                }
        self.assertRaisesRegex(ValueError,
                               "Invalid status 'freida' on bookmark creation; must be 'new' or 'submitted'",
                               self._create_bookmark,
                               **args)

    def test_create_bookmark__extra_args(self):
        """Verify create_bookmark raises if unrecognized args are provided.

        Note that even some Bookmark attributes are not allowed as args to create_bookmark.
        """
        args = {'summary': self._summary,
                'url': self._url,
                'display_date': self._display_date,
                'sort_date': datetime.utcnow(),
                'submitted_on': datetime.utcnow(),
                'ice_cream': 'chocolate'}
        self.assertRaisesRegex(
            ValueError,
            'Unexpected arguments provided for create_bookmark: ice_cream, sort_date, submitted_on',
            self._create_bookmark,
            **args)


class BookmarkSelectTests(BookmarkDaoTestCase):
    """Verify behavior of query methods.

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

        # No more records
        selected_bookmarks, cursor = Bookmark.select_bookmarks(cursor=cursor)
        self.assertEqual([], selected_bookmarks)
        self.assertIsNone(cursor)
        

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


class BookmarkUpdateTests(BookmarkDaoTestCase):
    """Verify update_bookmark behavior."""

    def test_update__simple(self):
        """Verify update of url, summary and description."""
        url = "http://latimes.com/news/article.html"
        summary = "Good article about weaving"
        description = "Learn how to weave your own fabric"

        # Create test bookmark and make sure our test data does not collide
        test_bookmark = self._create_test_bookmark()
        self.assertNotEqual(url, test_bookmark.url)
        self.assertNotEqual(summary, test_bookmark.summary)
        self.assertNotEqual(description, test_bookmark.description)

        # Update bookmark
        updated_bookmark = Bookmark.update_bookmark(
            test_bookmark.bookmark_id,
            summary=summary,
            url=url,
            description=description)
        self.assertIsNotNone(updated_bookmark)
        self.assertEqual(test_bookmark.bookmark_id, updated_bookmark.bookmark_id)

        # Clear session and re-select bookmark to verify that it was persisted
        self.session.flush()
        self.session.commit()
        selected_bookmark = self._select_bookmark(test_bookmark.bookmark_id)
        self.assertIsNotNone(selected_bookmark)

        # Verify changed and unchanged attributes
        for bookmark in (updated_bookmark, selected_bookmark):
            self.assertEqual(url, bookmark.url)
            self.assertEqual(summary, bookmark.summary)
            self.assertEqual(description, bookmark.description)

            # Verify that everything else stayed the same
            for attr in ('sort_date', 'display_date_format', 'status', 'created_on',
                         'submitted_on', 'topics'):
                self.assertEqual(getattr(test_bookmark, attr), getattr(bookmark, attr))
                                                    
    def test_update__clear_required_attr(self):
        """Verify that attempt to clear url, summary, or display_date_format raises."""
        # Create test bookmark
        test_bookmark = self._create_test_bookmark()

        # Attempt to clear required data
        for attr in ('url', 'summary', 'display_date', 'status'):
            for empty_val in ('', None):
                self.assertRaisesRegex(ValueError,
                                       "Cannot provide empty value or None for bookmark {0}".format(attr),
                                       Bookmark.update_bookmark,
                                       test_bookmark.bookmark_id, 
                                       **{attr: empty_val})

    def test_update__clear_optional_attr(self):
        """Verify that optional attributes can be cleared."""
        # Create test bookmark
        test_bookmark = self._create_test_bookmark(description='hi')
        self.assertEqual('hi', test_bookmark.description)

        # Clear description
        for empty_val in ('', None):
            updated_bookmark = Bookmark.update_bookmark(test_bookmark.bookmark_id, description=empty_val)
            self.assertIsNone(updated_bookmark.description)
        
    @patch.object(Bookmark, '_parse_display_date')
    def test_update__display_date(self, mock_parse_display_date):
        """Verify results and calls made when display_date is updated."""

        # Create test bookmark
        test_bookmark = self._create_test_bookmark()
        
        # Set up mocks
        new_sort_date = test_bookmark.sort_date + timedelta(hours=12)
        new_format = 'foo'
        mock_parse_display_date.return_value = (new_sort_date, new_format)

        # Update display_date
        updated_bookmark = Bookmark.update_bookmark(test_bookmark.bookmark_id, display_date='something')
        self.assertEqual(new_sort_date, updated_bookmark.sort_date)
        self.assertEqual(new_format, updated_bookmark.display_date_format)

        # Verify mock
        mock_parse_display_date.assert_called_once_with('something')

    @patch.object(Bookmark, 'update_status')
    def test_update__status(self, mock_update_status):
        """Verify that appropriate call is made when status is updated."""

        # Create test bookmark
        test_bookmark = self._create_test_bookmark()
        
        # Update status
        mock_status = Mock(name='updated_status')
        updated_bookmark = Bookmark.update_bookmark(test_bookmark.bookmark_id, status=mock_status)

        # Verify mock
        mock_update_status.assert_called_once_with(mock_status.lower())

    @patch.object(Bookmark, 'update_topics')
    def test_update__topics(self, mock_update_topics):
        """Verify that appropriate call is made when topics are updated."""

        # Create test bookmark
        test_bookmark = self._create_test_bookmark()
        
        # Update topics
        mock_topics = Mock(name='updated_topics')
        updated_bookmark = Bookmark.update_bookmark(test_bookmark.bookmark_id, topics=mock_topics)

        # Verify mock
        mock_update_topics.assert_called_once_with(mock_topics)

    def test_update__other_attrs(self):
        """Verify that attempt to update other attributes raises."""
        # Create test bookmark
        test_bookmark = self._create_test_bookmark()

        attrs = {'sort_date': datetime.utcnow(), 
                 'foo': 'hi',
                 'submitted_on': datetime.utcnow()}
        self.assertRaisesRegex(ValueError,
                               "Unexpected arguments provided for update_bookmark: foo, sort_date, submitted_on",
                               Bookmark.update_bookmark,
                               test_bookmark.bookmark_id, 
                               **attrs)

    @patch.object(BookmarkStatus, 'is_valid_status_transition')
    @patch.object(BookmarkStatus, 'is_valid_status')
    def test_update_status(self, mock_is_valid_status, mock_is_valid_transition):
        """Verify update_status method when status and transition are valid."""
        # Set up mocks
        mock_is_valid_status.return_value = True
        mock_is_valid_transition.return_value = True
        mock_new_status = 'new_status'

        # Create test bookmark and verify expected status
        test_bookmark = self._create_test_bookmark()
        self.assertEqual(BookmarkStatus.NEW, test_bookmark.status)

        # Update status
        test_bookmark.update_status(mock_new_status)
        self.assertEqual(mock_new_status, test_bookmark.status)

        # Verify mocks
        mock_is_valid_status.assert_called_once_with(mock_new_status)
        mock_is_valid_transition.assert_called_once_with(BookmarkStatus.NEW, mock_new_status)

    def test_update_status__submitted(self):
        """Verify update_status method sets submitted_on when status is updated to 'submitted.'"""
        # Create test bookmark and verify expected status
        test_bookmark = self._create_test_bookmark()
        self.assertEqual(BookmarkStatus.NEW, test_bookmark.status)
        self.assertIsNone(test_bookmark.submitted_on)

        # Update status
        test_bookmark.update_status(BookmarkStatus.SUBMITTED)
        self.assertEqual(BookmarkStatus.SUBMITTED, test_bookmark.status)
        self.assertIsNotNone(test_bookmark.submitted_on)

    def test_update_status__submitted_2x(self):
        """Verify update_status method only sets submitted_on once."""
        # Create test bookmark and verify expected status
        test_bookmark = self._create_test_bookmark()
        self.assertEqual(BookmarkStatus.NEW, test_bookmark.status)
        self.assertIsNone(test_bookmark.submitted_on)

        # Update status
        test_bookmark.update_status(BookmarkStatus.SUBMITTED)
        self.assertEqual(BookmarkStatus.SUBMITTED, test_bookmark.status)
        self.assertIsNotNone(test_bookmark.submitted_on)
        orig_submitted_on = test_bookmark.submitted_on

        # Update status to accepted
        test_bookmark.update_status(BookmarkStatus.ACCEPTED)
        self.assertEqual(BookmarkStatus.ACCEPTED, test_bookmark.status)
        self.assertEqual(orig_submitted_on, test_bookmark.submitted_on)

        # Update status back to submitted_on
        test_bookmark.update_status(BookmarkStatus.SUBMITTED)
        self.assertEqual(BookmarkStatus.SUBMITTED, test_bookmark.status)
        self.assertEqual(orig_submitted_on, test_bookmark.submitted_on)
        
    @patch.object(BookmarkStatus, 'is_valid_status', Mock(return_value=False))
    def test_update_status__invalid_status(self):
        """Verify update_status method when status is invalid."""
        # Set up mocks
        mock_new_status = 'new_status'

        # Create test bookmark
        test_bookmark = self._create_test_bookmark()

        # Update status
        self.assertRaisesRegex(
            ValueError,
            "Invalid bookmark status 'new_status'; must be one of 'new', 'submitted', 'accepted', 'rejected'",
            test_bookmark.update_status,
            mock_new_status)

    @patch.object(BookmarkStatus, 'is_valid_status_transition', Mock(return_value=False))
    @patch.object(BookmarkStatus, 'is_valid_status', Mock(return_value=True))
    def test_update_status__invalid_transition(self):
        """Verify update_status method when transition is invalid."""
        # Set up mocks
        mock_new_status = 'new_status'

        # Create test bookmark 
        test_bookmark = self._create_test_bookmark()

        # Update status
        self.assertRaisesRegex(
            ValueError,
            "Invalid bookmark status transition 'new' -> 'new_status'",
            test_bookmark.update_status,
            mock_new_status)

    def test_update_topics(self):
        """Verify that topics can be added, removed, and left alone."""
        test_bookmark = self._create_test_bookmark(topic_names=['keeper', 'loser'])
        self.assertEqual(2, len(test_bookmark.topics))
        self.assertEqual(set(['keeper', 'loser']), set([t.topic for t in test_bookmark.topics]))
        keeper_created_on = [t.created_on for t in test_bookmark.topics if t.topic == 'keeper'][0]

        # Update topics
        test_bookmark.update_topics(['new', 'keeper'])
        self.assertEqual(2, len(test_bookmark.topics))
        self.assertEqual(set(['keeper', 'new']), set([t.topic for t in test_bookmark.topics]))
        self.assertEqual(keeper_created_on, [t.created_on for t in test_bookmark.topics if t.topic == 'keeper'][0])
        self.session.merge(test_bookmark)

        # Verify that dropped topic is really gone
        topics = self.session.query(BookmarkTopic).filter_by(bookmark_id=test_bookmark.bookmark_id).all()
        self.assertEqual(set(['keeper', 'new']), set([t.topic for t in topics]))

    def test_update_topics__clear_topics__empty_list(self):
        """Verify that topics can be cleared by updating to empty list."""
        test_bookmark = self._create_test_bookmark(topic_names=['apple', 'banana'])
        self.assertEqual(2, len(test_bookmark.topics))

        # Update topics to empty list
        test_bookmark.update_topics([])
        self.assertEqual(0, len(test_bookmark.topics))
        self.session.merge(test_bookmark)

        # Verify that dropped topics are really gone
        topics = self.session.query(BookmarkTopic).filter_by(bookmark_id=test_bookmark.bookmark_id).all()
        self.assertEqual(0, len(topics))

    def test_update_topics__clear_topics__None(self):
        """Verify that topics can be cleared by updating to None."""
        test_bookmark = self._create_test_bookmark(topic_names=['apple', 'banana'])
        self.assertEqual(2, len(test_bookmark.topics))

        # Update topics to empty list
        test_bookmark.update_topics(None)
        self.assertEqual(0, len(test_bookmark.topics))
        self.session.merge(test_bookmark)

        # Verify that dropped topics are really gone
        topics = self.session.query(BookmarkTopic).filter_by(bookmark_id=test_bookmark.bookmark_id).all()
        self.assertEqual(0, len(topics))


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

    def test_bookmark_topic__association_proxy(self):
        """Verify BookmarkTopic creation via Bookmark.topic_names."""
        # Create and save bookmark first because of FK relationship
        test_bookmark = self._create_test_bookmark()
        test_bookmark.topic_names = [self._topic]
        self.session.merge(test_bookmark)
        self.session.flush()
        
        topics = self._select_bookmark_topics(self._bookmark_id)
        self.assertEqual(1, len(topics))
        self.assertEqual(self._topic, topics[0].topic)
        self.assertIsNotNone(topics[0].created_on)

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

    
        

        
