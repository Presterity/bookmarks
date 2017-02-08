"""Utility class for creating test DAO objects."""


from datetime import datetime
import uuid

from .bookmark_dao import Bookmark, BookmarkTopic, BookmarkNote


class TestDaoFactory(object):
    
    @classmethod
    def create_bookmark(cls, **kwargs) -> Bookmark:
        """Return Bookmark object.

        **kwargs are Bookmark attributes, i.e. bookmark_id, url, etc.
        """
        attrs = {'bookmark_id': uuid.uuid4(),
                 'url': 'http://news/articles/article12.html',
                 'summary': 'Mr. Ed says the Pledge of Allegiance',
                 'event_date': datetime.utcnow()}
        attrs.update(**kwargs)
        return Bookmark(**attrs)

    @classmethod
    def create_bookmark_topic(cls, **kwargs) -> BookmarkTopic:
        """Return BookmarkTopic.
        
        **kwargs are BookmarkTopic attributes; i.e. bookmark id, topic, and created_on.
        """
        attrs = {'bookmark_id': uuid.uuid4(),
                 'topic': 'Test Topic',
                 'created_on': datetime.utcnow}
        attrs.update(**kwargs)
        return BookmarkTopic(**attrs)

    @classmethod
    def create_bookmark_note(cls, **kwargs) -> BookmarkNote:
        """Return BookmarkNote.
        
        **kwargs are BookmarkNote attributes; i.e. note_id, bookmark id, text, etc.
        """
        attrs = {'note_id': uuid.uuid4(),
                 'bookmark_id': uuid.uuid4(),
                 'text': 'This is a test note.',
                 'author': 'Intrepid Volunteer',
                 'created_on': datetime.utcnow()}
        attrs.update(**kwargs)
        return BookmarkNote(**attrs)
