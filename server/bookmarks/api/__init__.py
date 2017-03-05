"""REST API for the bookmark manager.
"""

import logging
from typing import Optional, Any, Callable

from flask import Flask, jsonify, request

import bookmarks.dao as dao
from .response_formatter import ResponseFormatter


# Create Flask app and set up logging
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
logger = app.logger


# End request hook
#dao.Session.close(commit=True)


# API methods / endpoints
@app.route('/')
def root():
    return 'OK'

@app.route('/info')
def info():
    """Return structured information about the running application."""
    return jsonify({'nothing_to_see': 'not yet'})

@app.route("/api/1702/bookmark/", methods=['GET'])
def get_bookmarks():
    """Retrieve bookmarks, optionally filtered by topic.

    Optional topics are read from query string: topic=...&topic=...
    """
    topics = None
    if 'topic' in request.args:
        topics = request.args.getlist('topic')
    bookmarks = dao.Bookmark.select_bookmarks(topics=topics)
    response_data = ResponseFormatter.format_bookmarks_response(bookmarks, version=1702) 
    return jsonify(response_data), 200

@app.route("/api/1702/bookmark/<string:bookmark_id>", methods=['GET'])
def get_bookmark_by_id(bookmark_id):
    """Retrieve specific bookmark.
    """
    bookmark = dao.Bookmark.select_bookmark_by_id(bookmark_id)
    if not bookmark:
        response_json = ''
        status_code = 404
    else:
        response_json = jsonify(ResponseFormatter.format_bookmark(bookmark, version=1702))
        status_code = 200
    return response_json, status_code
