"""ORM representation of bookmark data model.
"""

from datetime import datetime
import logging
from typing import List, Tuple, Optional
import uuid

import sqlalchemy as sa
import sqlalchemy.ext.associationproxy as sa_assoc_proxy
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as sa_orm
import sqlalchemy.types as sa_types

from .session import Session
from .uuid_type import UUIDType

log = logging.getLogger(__name__)

__all__ = ('Bookmark',
           'BookmarkNote',
           'BookmarkTopic')

Base = declarative_base()


class Bookmark(Base):
    __tablename__ = 'bookmarks'

    DEFAULT_MAX_BOOKMARKS = 500

    bookmark_id = sa.Column(UUIDType(), primary_key=True, default=UUIDType.new_uuid)
    url = sa.Column(sa.String(2000), nullable=False)
    summary = sa.Column(sa_types.Text(), nullable=False)
    sort_date = sa.Column(sa_types.TIMESTAMP(timezone=True), nullable=False)
    description = sa.Column(sa_types.Text(), default=None)
    display_date_format = sa.Column(sa.String(20), nullable=False, default='%Y.%m.%d')
    status = sa.Column(sa.String(100), nullable=False, default='new')
    source = sa.Column(sa.String(50), default=None)
    source_item_id = sa.Column(sa.String(50), default=None)
    source_last_updated = sa.Column(sa_types.TIMESTAMP(timezone=True), default=None)
    submitter_id = sa.Column(sa.String(100), default=None)
    created_on = sa.Column(sa_types.TIMESTAMP(timezone=True), default=datetime.utcnow().replace(microsecond=0))
    submitted_on = sa.Column(sa_types.TIMESTAMP(timezone=True), default=None)

    @classmethod
    def _format_cursor(cls, sort_date: datetime, bookmark_id: str) -> str:
        """Generate string representation of cursor data used in select_bookmarks.

        :param sort_date: datetime that is the sort_date of the last record in the select result set
        :param bookmark_id: str that is the bookmark_id of the last record in the select result set
        """
        return '{0}|{1}'.format(sort_date.replace(tzinfo=None, microsecond=0).isoformat(), bookmark_id)
    
    @classmethod
    def _parse_cursor(cls, cursor: str) -> Tuple[datetime, str]:
        """Parse components out of cursor string provided to select_bookmarks.

        :param cursor: string generated by _format_cursor
        :return: tuple that is (sort_date, bookmark_id) for use in the select statement
        """
        toks = cursor.split('|')
        if len(toks) != 2:
            raise ValueError("Invalid cursor format; expected 'sort_date|bookmark_id' with sort_date in isoformat")
        try:
            sort_date = datetime.strptime(toks[0], '%Y-%m-%dT%H:%M:%S')
        except ValueError as ex:
            raise ValueError("Invalid cursor format; sort_date '{0}' not in expected format %Y-%m-%dT%H:%M:%S".format(toks[0]))
        return sort_date, toks[1]

    @classmethod
    def create_bookmark(cls, **kwargs) -> 'Bookmark':
        """Create, persist and return new Bookmark object.

        Required **kwargs:
          * summary: Brief description of bookmarked content
          * url: Location at which bookmarked content was found
          * display_date: Date to be associated with bookmarked event, in format %Y.%m[.%d [%H[:%M]]]

        Optional **kwargs:
          * description: More detailed information about bookmarked content
          * topics: List of strings that are presterity.org topic page names
          * bookmark_id: UUID to be assigned to bookmark; if not provided, database will assign automatically
          * status: String that is 'new' or 'submitted'

        :return: newly created and persisted Bookmark
        :raise: ValueError if required args are not specified
        :raise: ValueError if display_date is not in expected format
        :raise: ValueError if status is specified and something other than 'new' or 'submitted'
        :raise: ValueError if extra args are specified

        """
        for arg in ('summary', 'url', 'display_date'):
            if arg not in kwargs:
                raise ValueError("Missing required argument '{0}'".format(arg))

        sort_date, date_format_string = cls._parse_display_date(kwargs.pop('display_date'))

        attrs = {'bookmark_id': kwargs.pop('bookmark_id', uuid.uuid4()),
                 'url': kwargs.pop('url'),
                 'summary': kwargs.pop('summary'),
                 'sort_date': sort_date,
                 'display_date_format': date_format_string,
                 'status': 'new'}

        if 'description' in kwargs:
            attrs['description'] = kwargs.pop('description')
        if 'topics' in kwargs:
            attrs['topics'] = [BookmarkTopic(topic=t) for t in kwargs.pop('topics') or []]
        if 'status' in kwargs:
            status = kwargs.pop('status').lower()
            if status not in ('new', 'submitted'):
                raise ValueError("Invalid status '{0}' on bookmark creation; must be 'new' or 'submitted'".format(
                        status))
            attrs['status'] = status
            if status == 'submitted':
                attrs['submitted_on'] = datetime.utcnow().replace(microsecond=0)
        if kwargs:
            raise ValueError("Unexpected arguments provided for create_bookmark: {0}".format(
                    ', '.join(kwargs.keys())))

        new_bookmark = Bookmark(**attrs)

        session = Session.get()
        saved_bookmark = session.merge(new_bookmark)
        session.flush()
        return saved_bookmark

    @classmethod
    def select_bookmarks(cls, topics: List[str]=None, cursor=None, max_results=None) -> Tuple[List['Bookmark'], str]:
        """Select bookmarks, filtering by topics if specified, in ascending order by sort_date.

        If topics are specified, returned result is union of all Bookmarks associated 
        with at least one of specified topics.
        If cursor is specified, first returned result is result after record indicated by cursor.

        :param tags: option list of strings that are bookmark topics
        :param cursor: str returned from previous call to select_bookmarks
        :param max_results: int that is maximum number of results to return; default is cls.DEFAULT_MAX_BOOKMARKS

        :return: tuple that is list of Bookmarks (empty if no Bookmarks are found) and cursor string
        """
        session = Session.get()
        query = session.query(Bookmark)
        if topics:
            topic_query = session.query(BookmarkTopic.bookmark_id).filter(BookmarkTopic.topic.in_(topics))
            query = query.filter(Bookmark.bookmark_id.in_(topic_query.subquery()))
        if cursor:
            try:
                sort_date_limit, bookmark_id_limit = cls._parse_cursor(cursor)
                query = query.filter(sa.or_(Bookmark.sort_date > sort_date_limit,
                                            sa.and_(Bookmark.sort_date == sort_date_limit,
                                                    Bookmark.bookmark_id > bookmark_id_limit)))
            except ValueError as ex:
                log.exception("Cursor parse error; ignoring cursor", ex)
        query = query.order_by(Bookmark.sort_date, Bookmark.bookmark_id)
        query = query.limit(max_results or cls.DEFAULT_MAX_BOOKMARKS)
        results = query.all()
        cursor = None if not results else cls._format_cursor(results[-1].sort_date, results[-1].bookmark_id)
        return results, cursor

    @classmethod
    def select_bookmark_by_id(cls, bookmark_id: str) -> Optional['Bookmark']:
        """Select bookmark for specified id. 

        :param bookmark_id: string that is bookmark id
        :return: selected Bookmark or None if no such bookmark exists
        """
        query = Session.get().query(Bookmark).filter_by(bookmark_id=bookmark_id)
        return query.first()


    # private methods
    
    @classmethod
    def _parse_display_date(cls, display_date: str) -> Tuple[datetime, str]:
        """Parse provided date string into date and format string.

        Returned values are such that calling strftime on the returned date with the 
        returned format string will reproduce original display date.
        
        :param display_date: string that is date in format %Y[.%m[.%d[ %H[:%M]]]]
        :return: tuple that is parsed date and date format string
        :raise: ValueError if provided display_date is not in expected form
        """
        return (datetime.now(), '')
        

class BookmarkTopic(Base):
    __tablename__ = 'bookmark_topics'
    __table_args__ = (sa.ForeignKeyConstraint(['bookmark_id'], [Bookmark.bookmark_id]),)

    bookmark_id = sa.Column(UUIDType(), primary_key=True)
    topic = sa.Column(sa.String(100), nullable=False, primary_key=True)
    created_on = sa.Column(sa_types.TIMESTAMP(timezone=True), nullable=False, 
                           default=datetime.utcnow().replace(microsecond=0))
    

class BookmarkNote(Base):
    __tablename__ = 'bookmark_notes'
    __table_args__ = (sa.ForeignKeyConstraint(['bookmark_id'], [Bookmark.bookmark_id]),)

    note_id = sa.Column(UUIDType(), primary_key=True, default=UUIDType.new_uuid)
    bookmark_id = sa.Column(UUIDType(), nullable=False)
    text = sa.Column(sa_types.Text(), nullable=False)
    author = sa.Column(sa.String(100), nullable=False)
    created_on = sa.Column(sa_types.TIMESTAMP(timezone=True), nullable=False,
                           default=datetime.utcnow().replace(microsecond=0))


# Cascading delete is set up at DB level and is not re-specified here
Bookmark.topics = sa_orm.relationship(
    BookmarkTopic,
    primaryjoin=Bookmark.bookmark_id==BookmarkTopic.bookmark_id,
    order_by=lambda: (BookmarkTopic.topic, BookmarkTopic.created_on))

# Cascading delete is set up at DB level and is not re-specified here
Bookmark.notes = sa_orm.relationship(
    BookmarkNote,
    primaryjoin=Bookmark.bookmark_id==BookmarkNote.bookmark_id,
    order_by=lambda: BookmarkNote.created_on)