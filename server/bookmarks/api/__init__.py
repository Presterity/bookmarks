"""REST API for the bookmark manager.
"""

from typing import Optional, Any, Callable

import flask


# Create Flask app
app = flask.Flask(__name__)


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
    """Retrieve bookmarks, optionally filtered by tag.
    """
    return API.get_bookmarks(tags=tags, version=1702)

@app.route("/api/1702/bookmark/<string:bookmark_id>", methods=['GET'])
def get_bookmark_by_id(bookmark_id):
    """Retrieve specific bookmark.
    """
    return API.get_bookmark_by_id(bookmark_id, version=1702)

