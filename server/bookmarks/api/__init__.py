"""REST API for the bookmark manager.
"""

from typing import Optional, Any, Callable

from flask import Flask, jsonify

import bookmarks.dao as dao

# Create Flask app
app = Flask(__name__)


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
    """
    response_data = [ResponseFormatter.format_bookmark(b, version=1702) 
                     for b in dao.Bookmark.select_bookmarks()]
    return jsonify(response_data), 200

@app.route("/api/1702/bookmark/<string:bookmark_id>", methods=['GET'])
def get_bookmark_by_id(bookmark_id):
    """Retrieve specific bookmark.
    """
    bookmark = dao.Bookmark.select_bookmark_by_id(bookmark_id)
    if not bookmark:
        response_data = {'error': 'bookmark not found'}
        status_code = 404
    else:
        response_data = ResponseFormatter.format_bookmark(bookmark)
        status_code = 200
    return jsonify(response_data), 200 
