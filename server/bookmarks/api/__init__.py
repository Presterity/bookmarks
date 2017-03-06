"""REST API for the bookmark manager.
"""

import logging
from typing import Optional, Any, Callable

from flask import Flask, jsonify, request

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

@app.route("/api/<any_int(1702):version>/bookmark/", methods=['GET'])
def get_bookmarks(version=None):
    """Retrieve bookmarks, optionally filtered by topic.

    Optional topics are read from query string: topic=...&topic=...
    """
    topics = None
    if 'topic' in request.args:
        topics = request.args.getlist('topic')
    bookmarks = dao.Bookmark.select_bookmarks(topics=topics)
    response_data = ResponseFormatter.format_bookmarks_response(bookmarks, version=version) 
    return jsonify(response_data), 200

@app.route("/api/<any_int(1702):version>/bookmark/<string:bookmark_id>", methods=['GET'])
def get_bookmark_by_id(bookmark_id, version=None):
    """Retrieve specific bookmark.
    """
    bookmark = dao.Bookmark.select_bookmark_by_id(bookmark_id)
    if not bookmark:
        response_json = ''
        status_code = 404
    else:
        response_json = jsonify(ResponseFormatter.format_bookmark(bookmark, version=version))
        status_code = 200
    return response_json, status_code



