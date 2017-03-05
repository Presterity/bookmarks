"""Tests for BookmarkManager API endpoints.
"""

import unittest
from unittest.mock import Mock, patch
import uuid

import json

import bookmarks.dao as dao
from bookmarks.dao import TestDaoFactory
from bookmarks.api import app


class BookmarkManagerApiTests(unittest.TestCase):
    """Verify REST endpoints.
    """
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True 

    def get_bookmarks(self, topics=None):
        """Helper method to call Get Bookmarks API with specified topics.
        """
        uri = '/api/1702/bookmark/'
        if topics:
            uri += '?' + '&'.join(topics)
        return self.app.get(uri)

    @patch.object(dao.Bookmark, 'select_bookmarks')
    def test_get_bookmarks(self, mock_select_bookmarks):
        """Verify success scenario for retrieving bookmarks with no topics.
        """
        # Set up mocks and test data
        test_bookmarks = [TestDaoFactory.create_bookmark(), TestDaoFactory.create_bookmark()]
        mock_select_bookmarks.return_value = test_bookmarks
        
        # Make call
        response = self.get_bookmarks()
        
        print("\nRESPONSE")
        print(response.data)



