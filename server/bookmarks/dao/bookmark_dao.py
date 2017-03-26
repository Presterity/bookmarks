"""ORM representation of bookmark data model.
"""

from datetime import datetime
import logging
from typing import List, Tuple, Optional
import uuid

import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as sa_orm
import sqlalchemy.types as sa_types

from .bookmark_status import BookmarkStatus
from .exc import RecordNotFoundError
from .session import Session
from .date_parser import DateParser, DateParseError
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
    status = sa.Column(sa.String(100), nullable=False, default=BookmarkStatus.NEW)
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
        :raise: ValueError when the cursor wasn't correctly formatted
        """
        toks = cursor.split('|')
        if len(toks) != 2:
            raise ValueError("Invalid cursor format; expected 'sort_date|bookmark_id' with sort_date in isoformat")
        try:
            sort_date = datetime.strptime(toks[0], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            raise ValueError("Invalid cursor format; sort_date '{0}' not in expected format %Y-%m-%dT%H:%M:%S".format(
                    toks[0]))
        return sort_date, toks[1]

    @classmethod
    def create_bookmark(cls, **kwargs) -> 'Bookmark':
        """Create, persist and return new Bookmark object.

        :param **kwargs: dict of data described below

        Required **kwargs:
          * summary: Brief description of bookmarked content
          * url: Location at which bookmarked content was found
          * display_date: Date to be associated with bookmarked event, in format %Y[.%m[.%d [%H[:%M]]]]

        Optional **kwargs:
          * description: More detailed information about bookmarked content
          * topics: List of strings that are presterity.org topic page names
          * bookmark_id: UUID to be assigned to bookmark; if not provided, database will assign automatically
          * status: String that is 'new' or 'submitted'; default is 'new'

        :return: newly created and persisted Bookmark
        :raise: ValueError if required args are not specified
        :raise: ValueError if display_date is not in expected format
        :raise: ValueError if status is specified and something other than 'new' or 'submitted'
        :raise: ValueError if extra args are specified

        """
        for arg in ('summary', 'url', 'display_date'):
            if arg not in kwargs:
                raise ValueError("Missing required argument '{0}'".format(arg))

        # parse display date to get sort_date and display_date_format
        try:
            sort_date, display_date_format = DateParser.parse_date(kwargs.pop('display_date'))
        except DateParseError as parse_error:
            raise ValueError(str(parse_error))

        attrs = {'bookmark_id': kwargs.pop('bookmark_id', uuid.uuid4()),
                 'url': kwargs.pop('url'),
                 'summary': kwargs.pop('summary'),
                 'sort_date': sort_date,
                 'display_date_format': display_date_format,
                 'status': BookmarkStatus.NEW}

        if 'description' in kwargs:
            attrs['description'] = kwargs.pop('description')
        if 'topics' in kwargs:
            attrs['topic_names'] = kwargs.pop('topics') or []
        if 'status' in kwargs:
            status = kwargs.pop('status').lower()
            if not BookmarkStatus.is_valid_original_status(status):
                raise ValueError("Invalid status '{0}' on bookmark creation; must be {1}".format(
                        status, ' or '.join(["'{}'".format(s) for s in BookmarkStatus.VALID_ORIGINAL_STATUSES])))
            attrs['status'] = status
            if status == BookmarkStatus.SUBMITTED:
                attrs['submitted_on'] = datetime.utcnow().replace(microsecond=0)
        if kwargs:
            raise ValueError("Unexpected arguments provided for create_bookmark: {0}".format(
                    ', '.join(sorted(kwargs.keys()))))

        new_bookmark = Bookmark(**attrs)

        session = Session.get()
        saved_bookmark = session.merge(new_bookmark)
        session.flush()
        return saved_bookmark

    @classmethod
    def delete_bookmark(cls, bookmark_id) -> None:
        """Delete bookmark.

        If requested bookmark does not exist, do not raise. Fair assumption is that
        bookmark did exist and was already deleted. In any case, the desired result of
        the bookmark not existing is True if it isn't there in the first place.

        :param bookmark_id: UUID
        """
        if not bookmark_id:
            raise ValueError("Missing required argument 'bookmark_id'")
        Session.get().query(Bookmark).filter_by(bookmark_id=bookmark_id).delete()

    @classmethod
    def select_bookmarks(cls, topics: List[str]=None, cursor=None, max_results=None) -> Tuple[List['Bookmark'], str]:
        """Select bookmarks, filtering by topics if specified, in ascending order by sort_date.

        If topics are specified, returned result is union of all Bookmarks associated 
        with at least one of specified topics.
        If cursor is specified, first returned result is result after record indicated by cursor.

        :param topics: the list of topics to get bookmarks for. If empty, all topics are selected.
        :param tags: option list of strings that are bookmark topics
        :param cursor: str returned from previous call to select_bookmarks
        :param max_results: int that is maximum number of results to return; default is cls.DEFAULT_MAX_BOOKMARKS

        :return: tuple that is list of Bookmarks (empty if no Bookmarks are found) and cursor string
        :raise: ValueError if provided cursor was improperly formatted
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
                raise ex
        query = query.order_by(Bookmark.sort_date, Bookmark.bookmark_id)
        query = query.limit(max_results or cls.DEFAULT_MAX_BOOKMARKS)
        results = query.all()
        cursor = None if not results else cls._format_cursor(results[-1].sort_date, results[-1].bookmark_id)
        return results, cursor

    @classmethod
    def select_bookmark_by_id(cls, bookmark_id) -> Optional['Bookmark']:
        """Select bookmark for specified id. 

        :param bookmark_id: UUID or string that is bookmark id
        :return: selected Bookmark or None if no such bookmark exists
        """
        query = Session.get().query(Bookmark).filter_by(bookmark_id=bookmark_id)
        return query.first()

    @classmethod
    def update_bookmark(cls, bookmark_id, **kwargs) -> 'Bookmark':
        """Update, persist and return updated Bookmark object.

        Optional contents of **kwargs:
          * summary: Brief description of bookmarked content
          * url: Location at which bookmarked content was found
          * display_date: Date to be associated with bookmarked event, in format %Y.%m[.%d [%H[:%M]]]
          * description: More detailed information about bookmarked content
          * topics: List of strings that are presterity.org topic page names
          * status: String that is valid BookmarkStatus

        :param bookmark_id: string or UUID that identifies existing bookmark
        :param **kwargs: dict of optional data described above

        :return: updated Bookmark
        :raise: RecordNotFoundError if no such bookmark exists
        :raise: ValueError if required bookmark data is being set to empty value or None
        :raise: ValueError if display_date is specified and not in expected format
        :raise: ValueError if status is specified and an unsupported value or invalid transition
        :raise: ValueError if extra args are specified

        """
        bookmark = cls.select_bookmark_by_id(bookmark_id)
        if not bookmark:
            raise RecordNotFoundError("No bookmark by id {0}".format(bookmark_id))

        # Verify that required bookmark data is not being unset
        for attr in ('url', 'summary', 'display_date', 'status'):
            if attr in kwargs and not kwargs[attr]:
                raise ValueError("Cannot provide empty value or None for bookmark {0}".format(attr))

        # Update simple attributes
        for attr in [a for a in ('url', 'summary', 'description') if a in kwargs]:
            setattr(bookmark, attr, kwargs.pop(attr) or None)

        # If display_date is specified, it must be in expected format
        if 'display_date' in kwargs:
            sort_date, display_date_format = DateParser.parse_date(kwargs.pop('display_date'))
            bookmark.sort_date = sort_date
            bookmark.display_date_format = display_date_format

        # If status is specified, it must be valid and supported transition
        if 'status' in kwargs:
            bookmark.update_status(kwargs.pop('status').lower())

        # Update topics intelligently
        if 'topics' in kwargs:
            bookmark.update_topics(kwargs.pop('topics') or [])

        # If anything is left in kwargs, raise an error
        if kwargs:
            raise ValueError("Unexpected arguments provided for update_bookmark: {0}".format(
                    ', '.join(sorted(kwargs.keys()))))

        session = Session.get()
        updated_bookmark = session.merge(bookmark)
        session.flush()
        return updated_bookmark

    def update_status(self, new_status: str):
        """Update status field of bookmark if allowed. Note that the updated Bookmark is not persisted.

        :param new_status: string that is new BookmarkStatus

        :raise: ValueError if invalid status is provided
        :raise: ValueError if provided status is not valid transition
        """
        if not BookmarkStatus.is_valid_status(new_status):
            raise ValueError("Invalid bookmark status '{0}'; must be one of {1}".format(
                    new_status, ', '.join(["'{}'".format(s) for s in BookmarkStatus.VALID_STATUSES])))
        if not BookmarkStatus.is_valid_status_transition(self.status, new_status):
            raise ValueError("Invalid bookmark status transition '{0}' -> '{1}'".format(self.status, new_status))

        self.status = new_status
        if self.status == BookmarkStatus.SUBMITTED and not self.submitted_on:
            self.submitted_on = datetime.utcnow().replace(microsecond=0)

    def update_topics(self, topics: List[str]):
        """Update topics associated with bookmark. Note that the updated Bookmark is not persisted.

        If topic from provided list is not currently associated with bookmark, add it.
        If topic currently associated with bookmark is not in provided list, delete it.

        :param topics: List of strings that are topics associated with bookmark
        """
        if not topics:
            self.topics = []
        else:
            current_topics = set(self.topic_names)
            updated_topics = set(topics)
            self.topics = list(filter(lambda t: t.topic in updated_topics, self.topics))
            for new_topic in updated_topics.difference(current_topics):
                self.topics.append(BookmarkTopic(topic=new_topic))


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
    order_by=lambda: (BookmarkTopic.topic, BookmarkTopic.created_on),
    cascade="all, delete-orphan")

Bookmark.topic_names = association_proxy(
    'topics', 'topic',
    creator=lambda topic_name: BookmarkTopic(topic=topic_name))

# Cascading delete is set up at DB level and is not re-specified here
Bookmark.notes = sa_orm.relationship(
    BookmarkNote,
    primaryjoin=Bookmark.bookmark_id==BookmarkNote.bookmark_id,
    order_by=lambda: BookmarkNote.created_on,
    cascade="all, delete-orphan")
