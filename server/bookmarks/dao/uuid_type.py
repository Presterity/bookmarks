"""Custom UUID type.
"""

import uuid

import sqlalchemy.types as sa_types

__all__ = ('UUIDType',)


class UUIDType(sa_types.TypeDecorator):
    """http://docs.sqlalchemy.org/en/latest/core/custom_types.html#backend-agnostic-guid-type
    """
    impl = sa_types.CHAR

    def process_bind_param(self, value, dialect):
        if value:
            value = str(value)
        return value

    def process_result_value(self, value, dialect):
        if value:
            value = uuid.UUID(hex=value)
        return value

    @staticmethod
    def new_uuid():
        return str(uuid.uuid4())

