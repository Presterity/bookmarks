"""Custom path converters.
"""

import re
import werkzeug.routing 

class AnyIntConverter(werkzeug.routing.BaseConverter):
    """Matches one of the integers provided, e.g. <any_int(1,2,3):version>

    Modeled off of werkzeug.routing.AnyConverter

    :param map: the URL map
    :param items: this function accepts the possible ints as positional args
    """

    def __init__(self, map, *items):
        super(AnyIntConverter, self).__init__(map)
        self.regex = '(?:%s)' % '|'.join([str(x) for x in [int(i) for i in items]])
        
    def to_python(self, value):
        return int(value)

