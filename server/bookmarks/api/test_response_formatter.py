"""Tests for ResponseFormatter.
"""

import datetime
import pytz
import unittest
from unittest.mock import Mock, patch
import uuid

from bookmarks.dao import TestDaoFactory
from .response_formatter import ResponseFormatter


class ResponseFormatterTests(unittest.TestCase):
    def setUp(self):
        self._bookmark_dao_data = {
            'bookmark_id': uuid.uuid4(),
            'url': 'http://foo.com/a/b/c/',
            'summary': 'The bear went over the mountain',
            'sort_date': datetime.datetime(2017, 2, 22, 21, 11, tzinfo=pytz.utc),
            'description': 'foo bar baz',
            'display_date_format': '%Y.%m.%d',
            'status': 'squishy',
            'source': 'Raindrop',
            'source_item_id': '1357',
            'source_last_updated': datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
            'submitter_id': 'frodo',
            'submitted_on': datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
            }

    def test_format_bookmark__no_topics(self):
        """Verify dict generated by ResponseFormatter.format_bookmark."""
        serialized_attrs = ('bookmark_id', 'description', 'summary', 'status', 'url')
        expected_dict = {k: str(v) for (k,v) in self._bookmark_dao_data.items() 
                         if k in serialized_attrs}
        expected_dict['display_date'] = '2017.02.22'
        expected_dict['tld'] = 'foo.com'
        expected_dict['topics'] = []

        test_bookmark = TestDaoFactory.create_bookmark(**self._bookmark_dao_data)
        bookmark_dict = ResponseFormatter.format_bookmark(test_bookmark)
        self.assertEqual(expected_dict, bookmark_dict)

    def test_format_bookmark__topics(self):
        """Verify dict generated by ResponseFormatter.format_bookmark for bookmark with topics."""
        test_bookmark = TestDaoFactory.create_bookmark()
        def create_topic(topic):
            return TestDaoFactory.create_bookmark_topic(bookmark_id=test_bookmark.bookmark_id, 
                                                        topic=topic)
        test_bookmark.topics = [create_topic('Topic One'), create_topic('Topic Two')]

        bookmark_dict = ResponseFormatter.format_bookmark(test_bookmark)
        self.assertEqual(['Topic One', 'Topic Two'], bookmark_dict['topics'])

    @patch.object(ResponseFormatter, 'format_bookmark')
    def test_format_bookmarks_response(self, mock_format_bookmark):
        """Verify dict generated by ResponseFormatter.format_bookmarks_response.

        Also verify that version is passed through.
        """
        # Set up mocks and test data
        mock_format_bookmark.return_value = {}
        mock_bookmarks = [Mock(name='bookmark_1'), Mock(name='bookmark_2')]
        version = 444

        # Make call
        response_data = ResponseFormatter.format_bookmarks_response(mock_bookmarks, version=version)
        
        # Verify response data
        self.assertEqual({'bookmarks': [{}, {}]}, response_data)
        
        # Verify mocks
        call_args_list = mock_format_bookmark.call_args_list
        self.assertEqual(len(mock_bookmarks), len(call_args_list))
        for i, mock_bookmark in enumerate(mock_bookmarks):
            self.assertEqual(mock_bookmark, call_args_list[i][0][0])
            self.assertEqual(version, call_args_list[i][1]['version'])
