"""REST API for the bookmark manager.

All endpoint URLs are versioned with ints that are yymm, approximately indicating when the API was released 
or updated. Compromise between the human-friendliness of dates and conciseness.
"""

import logging

from flask import Flask, request, jsonify
from flask_api import status

import bookmarks.dao as dao
from .path_converters import AnyIntConverter
from .request_handlers import Handlers
from .response_formatter import ResponseFormatter

# API version numbers
VERSION_1702 = 1702
URI_PREFIX = '/api/<any_int({0}):version>'.format(VERSION_1702)

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


def uri_path_prefix(*versions):
    if len(versions) < 1:
        raise ValueError('must provide at least one version number')
    versions_str = ','.join([str(i) for i in versions])
    return '/api/<any_int({0}):version>'.format(versions_str)


def uri_path(suffix, *versions):
    prefix = uri_path_prefix(*versions)
    return '{0}/{1}'.format(prefix, suffix)


# Custom error handlers
@app.errorhandler(status.HTTP_404_NOT_FOUND)
def page_not_found(e):
    """Instead of the default 404 HTML, return empty response body"""
    return '', status.HTTP_404_NOT_FOUND


# API methods / endpoints
@app.route('/')
def root():
    return 'OK'


@app.route('/info')
def info():
    """Return structured information about the running application."""
    return jsonify({'nothing_to_see': 'not yet'})


@app.route(uri_path('bookmarks/', VERSION_1702), methods=['GET'])
def get_bookmarks(version=None):
    return Handlers.get_bookmarks(request, version)


@app.route(uri_path('bookmarks/<string:bookmark_id>', VERSION_1702), methods=['GET'])
def get_bookmark_by_id(bookmark_id, version):
    return Handlers.get_bookmark_by_id(bookmark_id, version)


@app.route(uri_path('bookmarks/', VERSION_1702), methods=['POST'])
def post_bookmark(version=None):
    return Handlers.post_bookmark(request, version)


@app.route(uri_path('bookmarks/<string:bookmark_id>', VERSION_1702), methods=['PUT'])
def put_bookmark(bookmark_id, version):
    return Handlers.put_bookmark(request, bookmark_id, version)


@app.route(uri_path('bookmarks/<string:bookmark_id>', VERSION_1702), methods=['DELETE'])
def delete_bookmark(bookmark_id, version):
    return Handlers.delete_bookmark(bookmark_id, version)
