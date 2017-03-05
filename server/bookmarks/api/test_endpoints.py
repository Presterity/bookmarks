"""Tests for BookmarkManager API endpoints.
"""

import unittest
from unittest.mock import ANY, Mock, patch
import uuid

import json

import bookmarks.dao
from bookmarks.dao import TestDaoFactory
import bookmarks.api


class BookmarkManagerApiTests(unittest.TestCase):
    """Verify REST endpoints.
    """
    def setUp(self):
        self.app = bookmarks.api.app.test_client()
        self.app.testing = True 

    def get_bookmarks(self, topics=None):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        uri = '/api/1702/bookmark/'
        if topics:
            uri += '?' + '&'.join(['topic={0}'.format(t) for t in topics])
        return self.app.get(uri)

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
        test_bookmarks = [TestDaoFactory.create_bookmark(), TestDaoFactory.create_bookmark()]
        mock_select_bookmarks.return_value = test_bookmarks
        mock_format_response.return_value = mock_response_json = {'test_key': 'test_value'}
        
        # Make call
        response = self.get_bookmarks()
        
        # Verify response
        self.assertEqual(mock_response_json, self.get_response_json(response))
        self.assertEqual(200, response.status_code)

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(topics=None)
        mock_format_response.assert_called_once_with(test_bookmarks, version=ANY)

    @patch.object(bookmarks.api.ResponseFormatter, 'format_bookmarks_response')
    @patch.object(bookmarks.dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks__topics(self, mock_select_bookmarks, mock_format_response):
        """Verify success scenario for retrieving bookmarks with topics.
        """
        # Set up mocks and test data
        test_bookmarks = [TestDaoFactory.create_bookmark(), TestDaoFactory.create_bookmark()]
        mock_select_bookmarks.return_value = test_bookmarks
        mock_format_response.return_value = mock_response_json = {'test_key': 'test_value'}
        
        # Make call
        response = self.get_bookmarks(topics=['topic_1', 'topic_2'])
        
        # Verify response
        self.assertEqual(mock_response_json, self.get_response_json(response))
        self.assertEqual(200, response.status_code)

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(topics=['topic_1', 'topic_2'])
        mock_format_response.assert_called_once_with(test_bookmarks, version=ANY)

    @patch.object(bookmarks.dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks__empty(self, mock_select_bookmarks):
        """Verify response for empty list of bookmarks.
        """
        # Set up mocks and test data
        mock_select_bookmarks.return_value = []
        
        # Make call
        response = self.get_bookmarks()
        
        # Verify response
        self.assertEqual({'bookmarks': []}, self.get_response_json(response))
        self.assertEqual(200, response.status_code)

        # Verify mocks
        mock_select_bookmarks.assert_called_once_with(topics=None)

