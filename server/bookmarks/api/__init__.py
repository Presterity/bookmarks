"""REST API for the bookmark manager.

All endpoint URLs are versioned with ints that are yymm, approximately indicating when the API was released 
or updated. Compromise between the human-friendliness of dates and conciseness.
"""

import logging

from flask import Flask, jsonify, request
from flask_api import status
from werkzeug.exceptions import BadRequest

import bookmarks.dao as dao
from .path_converters import AnyIntConverter
from .response_formatter import ResponseFormatter

# Create Flask app and set up basic logging
app = Flask(__name__)
app.logger.setLevel(logging.INFO)


# Register custom URL converters
app.url_map.converters['any_int'] = AnyIntConverter


# Database actions on startup and around each request
def before_first_request():
    dao.Session.initialize()


def before_request():
    dao.Session.get()


def after_request(response):
    dao.Session.close(commit=True)
    return response


# API methods / endpoints
@app.route('/')
def root():
    return 'OK'


@app.route('/info')
def info():
    """Return structured information about the running application."""
    return jsonify({'nothing_to_see': 'not yet'})


@app.route("/api/<any_int(1702):version>/bookmarks/", methods=['GET'])
def get_bookmarks(version=None):
    """Retrieve bookmarks, optionally filtered by topic.

    Optional topics are read from query string: topic=...&topic=...
    """
    topics = None
    if 'topic' in request.args:
        topics = request.args.getlist('topic')
    bookmarks = dao.Bookmark.select_bookmarks(topics=topics)
    response_data = ResponseFormatter.format_bookmarks_response(bookmarks, version=version) 
    return jsonify(response_data), status.HTTP_200_OK


@app.route("/api/<any_int(1702):version>/bookmarks/", methods=['POST'])
@app.route("/api/<any_int(1702):version>/bookmarks/<string:bookmark_id>", methods=['PUT'])
def post_bookmarks(bookmark_id=None, version=None):
    # TODO why not support creating a batch of bookmarks in POST? Request body would have an array of them.
    """Create a new bookmark and assign it a new UUID if one is not provided.

    Expected request body:
    {
      "summary"          : <string>
      "display_date"     : <string: YYYY, YYYY.mm, YYYY.mm.dd, YYYY.mm.dd HH, YYYY.mm.dd HH:MM>
      "url"              : <string>
      "description" [OPT]: <string>
      "topics"      [OPT]: [<string>, ...]
    }
    """
    # returns None if mimetype is not application/json. Throws BadRequest exception on malformed JSON.
    bookmark_json = request.get_json()
    if bookmark_json:
        if bookmark_id:
            bookmark_json['bookmark_id'] = bookmark_id
        try:
            bookmark = dao.Bookmark.create_bookmark(**bookmark_json)
        except ValueError:
            # issue 400 response when an expected attribute is missing
            # TODO include message specific to the failure?
            raise BadRequest()
        status_code = status.HTTP_200_OK
        response_data = {
            'bookmarks': [ResponseFormatter.format_bookmark(bookmark, version=version)]
        }
    else:
        response_data = {}
        status_code = status.HTTP_400_BAD_REQUEST

    return jsonify(response_data), status_code


@app.route("/api/<any_int(1702):version>/bookmarks/<string:bookmark_id>", methods=['GET'])
def get_bookmark_by_id(bookmark_id, version=None):
    """Retrieve specific bookmark.
    """
    bookmark = dao.Bookmark.select_bookmark_by_id(bookmark_id)
    if not bookmark:
        response_json = ''
        status_code = status.HTTP_404_NOT_FOUND
    else:
        response_json = jsonify(ResponseFormatter.format_bookmark(bookmark, version=version))
        status_code = status.HTTP_200_OK
    return response_json, status_code



