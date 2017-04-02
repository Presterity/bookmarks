"""Request handlers for the bookmark REST API

"""

from typing import List, Tuple, Union

from flask import jsonify, Request, Response
from flask_api import status
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound
from base64 import b64encode, b64decode
import binascii

import bookmarks.dao as dao
from .response_formatter import ResponseFormatter


class Handlers(object):
    """
    Handles bookmark API requests. Individual bookmarks have the following JSON format in responses, unless otherwise
    stated:

    {
      "bookmark_id" : <string>
      "summary"     : <string>
      "description" : <string>
      "display_date": <string: YYYY, YYYY.mm, YYYY.mm.dd, YYYY.mm.dd HH, YYYY.mm.dd HH:MM>
      "status"      : <string>
      "topics"      : [<string>, ...]
      "tld"         : <string>  # top-level domain
      "url"         : <string>
    }
    """

    # replacement characters for '+' and '/' in base64 encoding so it can be included in URLs
    _alt_base64_chars = b'$@'

    @classmethod
    def get_bookmarks(cls, request: Request, version: int=None) -> Tuple[Union[Response, str], int]:
        """Retrieve bookmarks, optionally filtered by topic.
        Response JSON looks like this:

        {
          "bookmarks"  : [<Bookmark JSON>, …]  # ordered ascending by sort_date
          "total_count": <int>
          "next_cursor": <string>
        }

        Optional query arguments:
        * one or more topic=<topic> arguments where topic is the name of a presterity.org topic page
        * count=<int> where count is the maximum number of results to return; a default max will be enforced
        * cursor=<string> where the string is a token provided in the previous response

        Response status codes:
        200 OK: bookmarks found and returned
        204 No Content: no bookmarks found

        :param request: the request to get bookmarks
        :param version: API version in the request
        :return: the response and HTTP status code
        :raise: BadRequest when the request is malformed or has invalid contents
        :raise: InternalServerError when there is a server bug
        """

        # TODO get bookmarks by date range
        topics = None
        if 'topic' in request.args:
            topics = request.args.getlist('topic')

        start_cursor = None
        if 'cursor' in request.args:
            start_cursor = cls._base64_decode(request.args['cursor'])

        max_results = None
        if 'count' in request.args:
            try:
                max_results = request.args.get('count', type=int)
            except ValueError:
                raise BadRequest('count must be a valid int. was: {0}'.format(request.args['count']))

        bookmarks, next_cursor = dao.Bookmark.select_bookmarks(topics=topics, cursor=start_cursor, max_results=max_results)
        if len(bookmarks) == 0:
            return '', status.HTTP_204_NO_CONTENT

        response_data = cls._format_bookmarks(bookmarks=bookmarks, version=version)

        if next_cursor:
            response_data['next_cursor'] = cls._base64_encode(next_cursor)

        # TODO include total_count in response (select count(*) query results)
        return jsonify(response_data), status.HTTP_200_OK

    @classmethod
    def post_bookmark(cls, request: Request, version: int=None) -> Tuple[Response, int]:
        """Create a new bookmark and assign it a new UUID if one is not provided.

        Expected request body:
        {
          "summary"          : <string>
          "display_date"     : <string: YYYY, YYYY.mm, YYYY.mm.dd, YYYY.mm.dd HH, YYYY.mm.dd HH:MM>
          "url"              : <string>
          "description" [OPT]: <string>
          "topics"      [OPT]: [<string>, ...]
        }

        :param request: the request to add a bookmark
        :param version: API version of the request
        :return: the response and HTTP status code
        :raise: BadRequest when the request is malformed or has invalid contents
        :raise: InternalServerError when there is a server bug
        """
        # TODO should we support creating a batch of bookmarks in POST? Request body would have an array of them.
        # TODO Response would need to allow for partial success

        bookmark_json = cls._request_json(request)
        try:
            bookmark = dao.Bookmark.create_bookmark(**bookmark_json)
        except ValueError as ve:
            raise BadRequest(str(ve))

        response_data = cls._format_bookmarks([bookmark], version)
        return jsonify(response_data), status.HTTP_200_OK

    @classmethod
    def put_bookmark(cls, request: Request, bookmark_id: str, version: int=None) -> Tuple[Response, int]:
        """Update an existing bookmark or create a new one, if none exists with the given ID. The expected request body
        format matches that of the post_bookmark method. When updating an existing bookmark, that all fields are
        optional.

        :param request: the flask HTTP request
        :param bookmark_id: ID of the bookmark to create or update
        :param version: API version of the request
        :return: the response and HTTP status code
        :raise: BadRequest when the request is malformed or has invalid contents
        :raise: InternalServerError when there is a server bug
        """
        bookmark_json = cls._request_json(request)

        try:
            try:
                # first, try updating existing bookmark
                bookmark = dao.Bookmark.update_bookmark(bookmark_id, **bookmark_json)
            except dao.exc.RecordNotFoundError:
                # bookmark doesn't exist, so create it
                bookmark_json['bookmark_id'] = bookmark_id
                bookmark = dao.Bookmark.create_bookmark(**bookmark_json)
        except ValueError as ve:
            raise BadRequest(str(ve))

        response_data = {
            'bookmarks': [cls._format_bookmark(bookmark, version)]
        }

        return jsonify(response_data), status.HTTP_200_OK

    @classmethod
    def delete_bookmark(cls, bookmark_id: str, version: int=None) -> Tuple[Union[Response, str], int]:
        """Delete the bookmark with the given ID. Do nothing if no bookmark with the ID exists.

        :param bookmark_id: ID of the bookmark to delete
        :param version: API version of the request
        :return: the response and HTTP status code
        :raise: BadRequest when the bookmark_id is missing (which should never happen as it's required in the URL)
        :raise: InternalServerError when there is a server bug
        """
        try:
            dao.Bookmark.delete_bookmark(bookmark_id)
        except ValueError as ve:
            raise BadRequest(str(ve))
        return '', status.HTTP_204_NO_CONTENT

    @classmethod
    def get_bookmark_by_id(cls, bookmark_id: str, version: int=None) -> Tuple[Response, int]:
        """Retrieve specific bookmark.

        :param bookmark_id: ID of the bookmark to get
        :param version: API version of the request
        :return: the response and HTTP status code
        :raise: BadRequest when the request is malformed or has invalid contents
        :raise: InternalServerError when there is a server bug
        :raise: NotFound if no bookmark found matching the bookmark_id
        """
        bookmark = dao.Bookmark.select_bookmark_by_id(bookmark_id)
        if not bookmark:
            raise NotFound

        response_json = jsonify(cls._format_bookmark(bookmark, version))
        return response_json, status.HTTP_200_OK

    # for internal use only
    @classmethod
    def _request_json(cls, request: Request) -> dict:
        """Parse request body as JSON, or raise BadRequest error

        :param req: the HTTP request
        :return: a dict containing the parsed JSON
        :raise: BadRequest when the request mimetype isn't application/json or the request body can't be parsed as JSON
        """
        json_dict = request.get_json()
        if not json_dict:
            raise BadRequest('mimetype must be application/json and body must be parseable JSON')
        return json_dict

    @classmethod
    def _format_bookmark(cls, bookmark: dao.Bookmark, version: int) -> dict:
        """Format a Bookmark object as response JSON. If formatting fails, raise

        :param bookmark:
        :param version:
        :return:
        :raise: InternalServerError when the Bookmark couldn't be formatted
        """
        try:
            return ResponseFormatter.format_bookmark(bookmark, version=version)
        except ValueError:
            raise InternalServerError

    @classmethod
    def _format_bookmarks(cls, bookmarks: List[dao.Bookmark], version: int) -> dict:
        """Format a list of Bookmark objects as response JSON. If formatting fails, raise

        :param bookmark:
        :param version:
        :return:
        :raise: InternalServerError when the Bookmark couldn't be formatted
        """
        try:
            return ResponseFormatter.format_bookmarks_response(bookmarks, version=version)
        except ValueError:
            raise InternalServerError

    @classmethod
    def _base64_decode(cls, encoded: str) -> str:
        """Decode a string that is base64 encoded

        :param encoded: the encoded data, as a string
        :return: the decoded data, as a string
        :raise: BadRequest if there was a problem during the decoding
        """
        try:
            decoded_bytes = b64decode(encoded, cls._alt_base64_chars, validate=True)
            return decoded_bytes.decode('utf-8')
        except (binascii.Error, UnicodeError):
            raise BadRequest('not a valid cursor')

    @classmethod
    def _base64_encode(cls, string: str) -> str:
        """Encode a string using base64

        :param string: the string to encode
        :return: the base64 encoded data, as a string
        :raise: InternalServerError if there was a problem with encoding
        """
        try:
            bytes_to_encode = bytes(string, 'utf-8')
            encoded_bytes = b64encode(bytes_to_encode, cls._alt_base64_chars)
            return encoded_bytes.decode('utf-8')
        except UnicodeError:
            raise InternalServerError
