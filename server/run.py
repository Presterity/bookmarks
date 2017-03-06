#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run Bookmark Manager REST services.
"""

from __future__ import unicode_literals

import argparse
import logging
import logging.handlers

from bookmarks.api import app

def parse_args():
    parser = argparse.ArgumentParser(
        description="Bookmark Manager REST services",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', default='8080', 
                        help='localhost port for application')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='debugging capability and verbose output')
    return parser.parse_args()

def setup_logging(level=logging.INFO):

    # Set basic log level
    app.logger.setLevel(level)

    # Log to file
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = logging.handlers.RotatingFileHandler('bookmarks.log', backupCount=23)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Configure application logs
    logging.getLogger(__name__).setLevel(level)
    logging.getLogger(__name__).addHandler(handler)


if __name__ == "__main__":
    args = parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    setup_logging(level=log_level)
    port = int(args.port)
    app.run(host='localhost', port=port, debug=args.verbose)
