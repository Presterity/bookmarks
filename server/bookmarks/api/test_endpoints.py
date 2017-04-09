"""Tests for BookmarkManager API endpoints.
"""

import json
import unittest
import uuid
from unittest.mock import ANY, Mock, patch

from flask_api import status

import bookmarks.api
import bookmarks.dao


class BookmarkManagerApiTests(unittest.TestCase):
    """Verify REST endpoints.
    """
    def setUp(self):
        self.app = bookmarks.api.app.test_client()
        self.app.testing = True 

    def get_bookmarks(self, topics=None, cursor=None, version=1702):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        uri = '/api/{0}/bookmarks/'.format(version)
        if topics:
            uri += '?' + '&'.join(['topic={0}'.format(t) for t in topics])

        if cursor:
            uri += '&cursor={0}'.format(cursor)
        return self.app.get(uri)

    def get_bookmark_by_id(self, bookmark_id, version=1702):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        return self.app.get('/api/{0}/bookmarks/{1}'.format(version, bookmark_id))

    def post_bookmark(self, bookmark, version=1702):
        """Helper method to call POST bookmarks API"""
        return self.app.post('/api/{0}/bookmarks/'.format(version), data=json.dumps(bookmark),
                             content_type='application/json')

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
        mock_cursor = 'bW9ja19jdXJzb3I='  # base64 encoding of 'mock_cursor'
        mock_bookmarks = [Mock(name='bookmark_1'), Mock(name='bookmark_2')]
        mock_select_bookmarks.return_value = (mock_bookmarks, mock_cursor)
        mock_format_response.return_value = mock_response_json = {'test_key': 'test_value'}
        
        # Make call
        response = self.get_bookmarks()
        
        # Verify response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(mock_response_json, self.get_response_json(response))

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(topics=None, cursor=None, max_results=None)
        mock_format_response.assert_called_once_with(mock_bookmarks, version=1702)

    @patch.object(bookmarks.api.ResponseFormatter, 'format_bookmarks_response')
    @patch.object(bookmarks.dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks__topics(self, mock_select_bookmarks, mock_format_response):
        """Verify success scenario for retrieving bookmarks with topics.
        """
        # Set up mocks and test data
        mock_cursor = 'bW9ja19jdXJzb3I=' # base64 encoding of 'mock_cursor'
        mock_bookmarks = [Mock(name='bookmark_1'), Mock(name='bookmark_2')]
        mock_select_bookmarks.return_value = (mock_bookmarks, mock_cursor)
        mock_format_response.return_value = mock_response_json = {'test_key': 'test_value'}
        
        # Make call
        response = self.get_bookmarks(topics=['topic_1', 'topic_2'])
        
        # Verify response
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(mock_response_json, self.get_response_json(response))

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(cursor=None, max_results=None, topics=['topic_1', 'topic_2'])
        mock_format_response.assert_called_once_with(mock_bookmarks, version=ANY)

    @patch.object(bookmarks.dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks__empty(self, mock_select_bookmarks):
        """Verify response for empty list of bookmarks.
        """
        # Set up mocks and test data
        mock_select_bookmarks.return_value = ([], None)
        
        # Make call
        response = self.get_bookmarks()
        
        # Verify response
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(cursor=None, max_results=None, topics=None)

    def test_get_bookmarks__unavailable_version(self):
        """Verify 404 if invalid version is supplied.
        """
        response = self.get_bookmarks(version=1)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

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
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({'bookmark': 'that I am'}, self.get_response_json(response))

        # Verify mocks
        mock_select_bookmark.assert_called_once_with(str(bookmark_id))
        mock_format_bookmark.assert_called_once_with(bookmark=mock_bookmark, version=1702)

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
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(b'', response.data)

    def test_get_bookmark_by_id__unavailable_version(self):
        """Verify 404 if invalid version is supplied.
        """
        response = self.get_bookmark_by_id(uuid.uuid4(), version=1)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @patch.object(bookmarks.api.ResponseFormatter, 'format_bookmark')
    @patch.object(bookmarks.dao.Bookmark, 'create_bookmark')
    def test_post_bookmark(self, mock_create_bookmark, mock_format_response):
        bookmark_from_dao = {'new-bookmark': 123}
        mock_create_bookmark.return_value = bookmark_from_dao
        mock_format_response.return_value = {'some-bookmark': 'hi'}

        response = self.post_bookmark({'dummy': 123})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({'some-bookmark': 'hi'}, self.get_response_json(response))

        mock_create_bookmark.assert_called_once_with(dummy=123)
        mock_format_response.assert_called_once_with(bookmark=bookmark_from_dao, version=1702)



