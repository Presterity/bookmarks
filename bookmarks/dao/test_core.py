"""
Tests for core DAO methods.
"""

import unittest
from unittest.mock import patch, Mock

import sqlalchemy
from sqlalchemy.sql import text

import dao.core as core
import dao.settings as settings


class BaseDaoTest(unittest.TestCase):
    """Tests for base DAO methods."""

    def setUp(self):
        """Reset core._engine to None."""
        core._engine = None

    def test_connection(self):
        """Test that we can connect to the db."""
        connection = core.get_connection()
        ping = connection.execute(text("SELECT 'ping' AS pong")).fetchone()['pong']
        self.assertEqual(ping, "ping")

    @patch.object(sqlalchemy, 'create_engine')
    def test_ensure_engine__singleton(self, mock_create_engine):
        """Verify that _ensure_engine makes expected calls."""
        mock_create_engine.return_value = mock_engine = Mock(name='engine')
        engine = core._engine
        self.assertEqual(mock_engine, engine)
        mock_create_engine.assert_called_once_with(settings.PRESTERITY_DB_URL)

    @patch.object(sqlalchemy, 'create_engine')
    def test_ensure_engine__singleton(self, mock_create_engine):
        """Verify that ensure_engine only connects one time."""
        mock_create_engine.return_value = mock_engine = Mock(name='engine')
        engine = core._ensure_engine()
        self.assertEqual(mock_engine, engine)
        self.assertEqual(1, mock_create_engine.call_count)

        # Second time, create_engine should not be called
        engine = core._ensure_engine()
        self.assertEqual(mock_engine, engine)
        self.assertEqual(1, mock_create_engine.call_count)

