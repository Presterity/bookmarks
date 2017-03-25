"""REST API for the bookmark manager.

All endpoint URLs are versioned with ints that are yymm, approximately indicating when the API was released 
or updated. Compromise between the human-friendliness of dates and conciseness.
"""

import logging

from flask import Flask, request, jsonify

import bookmarks.dao as dao
from .path_converters import AnyIntConverter, AnyApiVersionConverter
from .request_handlers import Handlers
from .response_formatter import ResponseFormatter

# Create Flask app and set up basic logging
app = Flask(__name__)
app.logger.setLevel(logging.INFO)


# Register custom URL converters
app.url_map.converters['any_int'] = AnyIntConverter
app.url_map.converters['any_version'] = AnyApiVersionConverter


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


@app.route("/api/<any_version:version>/bookmarks/", methods=['GET'])
def get_bookmarks(version=None):
    return Handlers.get_bookmarks(request, version)


@app.route("/api/<any_version:version>/bookmarks/<string:bookmark_id>", methods=['GET'])
def get_bookmark_by_id(bookmark_id, version):
    return Handlers.get_bookmark_by_id(bookmark_id, version)


@app.route("/api/<any_version:version>/bookmarks/", methods=['POST'])
def post_bookmark(version=None):
    return Handlers.post_bookmark(request, version)


@app.route("/api/<any_version:version>/bookmarks/<string:bookmark_id>", methods=['PUT'])
def put_bookmark(bookmark_id, version):
    return Handlers.put_bookmark(request, bookmark_id, version)


@app.route("/api/<any_version:version>/bookmarks/<string:bookmark_id>", methods=['DELETE'])
def delete_bookmark(bookmark_id, version):
    return Handlers.delete_bookmark(bookmark_id, version)
