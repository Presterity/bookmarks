"""Tests for BookmarkManager API endpoints.
"""

import unittest
from unittest.mock import ANY, Mock, patch
import uuid

import json

import bookmarks.dao
import bookmarks.api


class BookmarkManagerApiTests(unittest.TestCase):
    """Verify REST endpoints.
    """
    def setUp(self):
        self.app = bookmarks.api.app.test_client()
        self.app.testing = True 

    def get_bookmarks(self, topics=None, version=1702):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        uri = '/api/{0}/bookmark/'.format(version)
        if topics:
            uri += '?' + '&'.join(['topic={0}'.format(t) for t in topics])
        return self.app.get(uri)

    def get_bookmark_by_id(self, bookmark_id, version=1702):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        return self.app.get('/api/{0}/bookmark/{1}'.format(version, bookmark_id))

    def get_response_json(self, response):
        """Extract response data as JSON.
        """
        return json.loads(response.data.decode(encoding='utf-8'))

    @patch.object(bookmarks.api.ResponseFormatter, 'format_bookmarks_response')
    @patch.object(bookmarks.dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks(self, mock_select_bookmarks, mock_format_response):
        """Verify success scenario for retrieving bookmarks with no topics.
        """
        # Set up mocks and test data
        mock_bookmarks = [Mock(name='bookmark_1'), Mock(name='bookmark_2')]
        mock_select_bookmarks.return_value = mock_bookmarks
        mock_format_response.return_value = mock_response_json = {'test_key': 'test_value'}
        
        # Make call
        response = self.get_bookmarks()
        
        # Verify response
        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response_json, self.get_response_json(response))

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(topics=None)
        mock_format_response.assert_called_once_with(mock_bookmarks, version=ANY)

    @patch.object(bookmarks.api.ResponseFormatter, 'format_bookmarks_response')
    @patch.object(bookmarks.dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks__topics(self, mock_select_bookmarks, mock_format_response):
        """Verify success scenario for retrieving bookmarks with topics.
        """
        # Set up mocks and test data
        mock_bookmarks = [Mock(name='bookmark_1'), Mock(name='bookmark_2')]
        mock_select_bookmarks.return_value = mock_bookmarks
        mock_format_response.return_value = mock_response_json = {'test_key': 'test_value'}
        
        # Make call
        response = self.get_bookmarks(topics=['topic_1', 'topic_2'])
        
        # Verify response
        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_response_json, self.get_response_json(response))

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(topics=['topic_1', 'topic_2'])
        mock_format_response.assert_called_once_with(mock_bookmarks, version=ANY)

    @patch.object(bookmarks.dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks__empty(self, mock_select_bookmarks):
        """Verify response for empty list of bookmarks.
        """
        # Set up mocks and test data
        mock_select_bookmarks.return_value = []
        
        # Make call
        response = self.get_bookmarks()
        
        # Verify response
        self.assertEqual(200, response.status_code)
        self.assertEqual({'bookmarks': []}, self.get_response_json(response))

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(topics=None)

    def test_get_bookmarks__unavailable_version(self):
        """Verify 404 if invalid version is supplied.
        """
        response = self.get_bookmarks(version=1)
        self.assertEqual(404, response.status_code)

    @patch.object(bookmarks.api.ResponseFormatter, 'format_bookmark')
    @patch.object(bookmarks.dao.Bookmark, 'select_bookmark_by_id')
    def test_get_bookmarks_by_id(self, mock_select_bookmark, mock_format_bookmark):
        """Verify calls and response for get_bookmark_by_id.
        """
        # Set up mocks and test data
        bookmark_id = uuid.uuid4()
        mock_select_bookmark.return_value = mock_bookmark = Mock(name='mock_bookmark')
        mock_format_bookmark.return_value = {'bookmark': 'that I am'}
        
        # Make call
        response = self.get_bookmark_by_id(bookmark_id)

        # Verify response
        self.assertEqual(200, response.status_code)
        self.assertEqual({'bookmark': 'that I am'}, self.get_response_json(response))

        # Verify mocks
        mock_select_bookmark.assert_called_once_with(str(bookmark_id))
        mock_format_bookmark.assert_called_once_with(mock_bookmark, version=ANY)

    @patch.object(bookmarks.dao.Bookmark, 'select_bookmark_by_id')
    def test_get_bookmarks_by_id__not_found(self, mock_select_bookmark):
        """Verify response for get_bookmark_by_id when no such bookmark exists.
        """
        # Set up mocks and test data
        bookmark_id = uuid.uuid4()
        mock_select_bookmark.return_value = None
        
        # Make call
        response = self.get_bookmark_by_id(bookmark_id)

        # Verify response
        self.assertEqual(404, response.status_code)
        self.assertEqual(b'', response.data)

    def test_get_bookmark_by_id__unavailable_version(self):
        """Verify 404 if invalid version is supplied.
        """
        response = self.get_bookmark_by_id(uuid.uuid4(), version=1)
        self.assertEqual(404, response.status_code)

