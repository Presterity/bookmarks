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

    def get_bookmarks(self, topics=None, cursor=None, version=bookmarks.api.VERSION_1702):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        uri = '/api/{0}/bookmarks/'.format(version)
        if topics:
            uri += '?' + '&'.join(['topic={0}'.format(t) for t in topics])

        if cursor:
            uri += '&cursor={0}'.format(cursor)
        return self.app.get(uri)

    def get_bookmark_by_id(self, bookmark_id, version=bookmarks.api.VERSION_1702):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        return self.app.get('/api/{0}/bookmarks/{1}'.format(version, bookmark_id))

    def post_bookmark(self, bookmark, version=bookmarks.api.VERSION_1702):
        """Helper method to call POST bookmarks API"""
        return self.app.post('/api/{0}/bookmarks/'.format(version), data=json.dumps(bookmark),
                             content_type='application/json')

    def put_bookmark(self, bookmark_id, bookmark, version=bookmarks.api.VERSION_1702):
        """Helper method to call PUT bookmarks API"""
        return self.app.put('/api/{0}/bookmarks/{1}'.format(version, bookmark_id), data=json.dumps(bookmark),
                            content_type='application/json')

    def delete_bookmark(self, bookmark_id, version=bookmarks.api.VERSION_1702):
        """Helper method to call DELETE bookmarks API"""
        return self.app.delete('/api/{0}/bookmarks/{1}'.format(version, bookmark_id))

    def get_response_str(self, response):
        return response.data.decode(encoding='utf-8')

    def make_bookmark(self):
        return {
            'summary': 'this is a summary',
            'display_date': '2017.04.01',
            'url': 'http://example.com/news',
            'description': 'even more stuff about the thing',
            'topics': ['cows', 'sheep', 'dogs']
        }

    def make_bookmark_response(self, bookmark_id):
        bookmark = self.make_bookmark()
        bookmark['bookmark_id'] = str(bookmark_id)
        bookmark['tld'] = 'example.com'
        bookmark['status'] = 'new'

        return bookmark

    def get_response_json(self, response):
        """Extract response data as JSON.
        """
        return json.loads(self.get_response_str(response))

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
        mock_format_response.assert_called_once_with(mock_bookmarks, version=bookmarks.api.VERSION_1702)

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
        mock_select_bookmark.assert_called_once_with(bookmark_id)
        mock_format_bookmark.assert_called_once_with(bookmark=mock_bookmark, version=bookmarks.api.VERSION_1702)

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

    @patch.object(bookmarks.dao.Bookmark, 'select_bookmark_by_id')
    def test_get_bookmarks_by_id__id_must_be_uuid(self, mock_select_bookmark):
        """Verify response for get_bookmark_by_id when provided id is not a uuid.
        """
        # Set up mocks and test data
        bookmark_id = "bob"
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
        mock_format_response.assert_called_once_with(bookmark=bookmark_from_dao, version=bookmarks.api.VERSION_1702)

    @patch.object(bookmarks.dao.Bookmark, 'create_bookmark')
    def test_post_bookmark__bad_request(self, mock_create_bookmark):
        mock_create_bookmark.side_effect = ValueError('something bad happened')

        response = self.post_bookmark({'dummy': 123})

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('400 Bad Request: something bad happened', self.get_response_str(response))

        mock_create_bookmark.assert_called_once_with(dummy=123)

    def assert_missing_post(self, field):
        """Makes sure that when required field is missing, the API returns a 400 response"""
        bookmark = self.make_bookmark()
        bookmark.pop(field)

        response = self.post_bookmark(bookmark)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("400 Bad Request: Missing required argument '{0}'".format(field),
                         self.get_response_str(response))

    def test_post_bookmark__missing_summary(self):
        self.assert_missing_post('summary')

    def test_post_bookmark__missing_url(self):
        self.assert_missing_post('url')

    def test_post_bookmark__missing_display_date(self):
        self.assert_missing_post('display_date')

    def test_post_bookmark_invalid_display_date(self):
        """If display date doesn't have valid format, assert that 400 response is returned"""
        bookmark = self.make_bookmark()
        bookmark['display_date'] = 'I am not a date'

        response = self.post_bookmark(bookmark)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual("400 Bad Request: can't parse date from: \"I am not a date\"",
                         self.get_response_str(response))

    def test_delete_bookmark_nonexistent(self):
        """Check that nonexistent bookmark delete returns 204"""
        response = self.delete_bookmark(uuid.uuid4())

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual('', self.get_response_str(response))

    def test_delete_bookmark_no_id(self):
        """Check that bookmark delete with no ID returns 405"""
        response = self.app.delete('/api/{0}/bookmarks/'.format(bookmarks.api.VERSION_1702))

        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    @patch.object(bookmarks.api.ResponseFormatter, 'format_bookmark')
    @patch.object(bookmarks.dao.Bookmark, 'create_bookmark')
    @patch.object(bookmarks.dao.Bookmark, 'update_bookmark')
    def test_put_bookmark_nonexistent(self, mock_update_bookmark, mock_create_bookmark, mock_format_bookmark):
        """Check that nonexistent bookmark is added"""
        bookmark = self.make_bookmark()
        bookmark_id = uuid.uuid4()
        mock_formatted_bookmark = self.make_bookmark_response(bookmark_id)

        mock_update_bookmark.side_effect = bookmarks.dao.exc.RecordNotFoundError('no such bookmark')
        mock_create_bookmark.return_value = {}
        mock_format_bookmark.return_value = mock_formatted_bookmark

        response = self.put_bookmark(bookmark_id, bookmark)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(mock_formatted_bookmark, self.get_response_json(response))

    def test_put_bookmark_nonexistent(self):
        """Check that bookmark with bad id is not added"""
        bookmark = self.make_bookmark()
        bookmark_id = ""

        response = self.put_bookmark(bookmark_id, bookmark)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
