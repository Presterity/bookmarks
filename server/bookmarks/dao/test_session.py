"""
Tests for Session.
"""

import unittest
from unittest.mock import patch, Mock

import sqlalchemy.orm as sa_orm
from sqlalchemy.sql import text

from .session import Session
from .settings import PRESTERITY_DB_URL


class SessionTest(unittest.TestCase):
    """Tests for Session utility class."""

    def setUp(self):
        """Reset Session._session to None."""
        Session._session = None

    def test_initialize(self):
        """Test Session initialization."""
        self.assertIsNone(Session._session)
        Session.initialize()
        self.assertIsNotNone(Session._session)

    def test_get(self):
        """Verify that Session.get returns working session."""
        session = Session.get()
        self.assertIsNotNone(session)
        self.assertTrue(isinstance(session, sa_orm.scoped_session))

        ping = session.connection().execute(text("SELECT 'ping' AS pong")).fetchone()['pong']
        self.assertEqual(ping, "ping")

    @patch.object(Session, 'initialize')
    def test_get__initialize(self, mock_initialize):
        """Verify that Session.get initializes session iff necessary."""
        self.assertIsNone(Session._session)
        Session.get()
        mock_initialize.assert_called_once_with()
        mock_initialize.reset_mock()

        Session._session = Mock(name='mock_session')
        Session.get()
        self.assertEqual(0, mock_initialize.call_count)

    def test_get__idempotent(self):
        """Verify that scoped session is the same each time Session.get is called."""
        session_1 = Session.get()
        session_2 = Session.get()
        self.assertTrue(session_1 is session_2)

    def test_close__commit(self):
        """Verify that close calls commit if requested before releasing session back to connection pool."""
        mock_session = Mock(name='mock_session',
                            commit=Mock(),
                            remove=Mock())
        Session._session = mock_session
        Session.close(commit=True)
        mock_session.remove.assert_called_once_with()
        mock_session.commit.assert_called_once_with()

    def test_close__no_commit(self):
        """Verify that close does not call commit if not requested before releasing session."""
        mock_session = Mock(name='mock_session',
                            commit=Mock(),
                            remove=Mock())
        Session._session = mock_session
        Session.close(commit=False)
        mock_session.remove.assert_called_once_with()
        self.assertEqual(0, mock_session.commit.call_count)

    def test_close__no_session(self):
        """Verify that calling close does no harm if no session exists, neither Session.initialize nor get was ever called."""
        self.assertIsNone(Session._session)
        Session.close()
        self.assertIsNone(Session._session)
