"""ORM representation of bookmark data model.
"""

import sqlalchemy as sa
import sqlalchemy.ext.associationproxy as sa_assoc_proxy
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as sa_orm
import sqlalchemy.types as sa_types

from .uuid_type import UUIDType


__all__ = ('Bookmark',
           'BookmarkNote',
           'BookmarkTopic')

Base = declarative_base()


class Bookmark(Base):
    __tablename__ = 'bookmarks'

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
    submission_date = sa.Column(sa_types.TIMESTAMP(timezone=True), default=None)
    

class BookmarkTopic(Base):
    __tablename__ = 'bookmark_topics'
    __table_args__ = (sa.ForeignKeyConstraint(['bookmark_id'], [Bookmark.bookmark_id]),)

    bookmark_id = sa.Column(UUIDType(), primary_key=True)
    topic = sa.Column(sa.String(100), nullable=False, primary_key=True)
    created_on = sa.Column(sa_types.TIMESTAMP(timezone=True), nullable=False)
    

class BookmarkNote(Base):
    __tablename__ = 'bookmark_notes'
    __table_args__ = (sa.ForeignKeyConstraint(['bookmark_id'], [Bookmark.bookmark_id]),)

    note_id = sa.Column(UUIDType(), primary_key=True, default=UUIDType.new_uuid)
    bookmark_id = sa.Column(UUIDType(), nullable=False)
    text = sa.Column(sa_types.Text(), nullable=False)
    author = sa.Column(sa.String(100), nullable=False)
    created_on = sa.Column(sa_types.TIMESTAMP(timezone=True), nullable=False)


Bookmark.topics = sa_orm.relationship(
    BookmarkTopic,
    primaryjoin=Bookmark.bookmark_id==BookmarkTopic.bookmark_id,
    order_by=lambda: (BookmarkTopic.topic, BookmarkTopic.created_on))

Bookmark.notes = sa_orm.relationship(
    BookmarkNote,
    primaryjoin=Bookmark.bookmark_id==BookmarkNote.bookmark_id,
    order_by=lambda: BookmarkNote.created_on)
