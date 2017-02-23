"""Transformations of DAOs into dicts ready for serialization.
"""

import tldextract

import bookmarks.dao as dao


class ResponseFormatter(object):
    
    @classmethod
    def format_bookmark(cls, bookmark: dao.Bookmark) -> dict:
        """Transform Bookmark object into dict to be serialized into response data.

        Expected format:
        {
          "bookmark_id" : <str>,
          "description" : <str>,
          "display_date": <str that is date for display, e.g. '201701'>,
          "summary"     : <str>,
          "sort_date"   : <str that is utc date in isoformat>,
          "status"      : <str>,
          "topics"      : [<str>, ...],
          "tld"         : <str that is top-level domain, e.g. 'cnn.com'>,
          "url"         : <str>
        }

        """
        d = {}
        for attr in ('bookmark_id', 'description', 'summary', 'status', 'url'):
            d[attr] = str(getattr(bookmark, attr))
        d['sort_date'] = bookmark.sort_date.isoformat()
        d['display_date'] = bookmark.sort_date.strftime(bookmark.display_date_format)
        d['tld'] = tldextract.extract(bookmark.url).registered_domain
        d['topics'] = [t.topic for t in bookmark.topics]
        return d
