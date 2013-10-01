# -*- coding: utf-8 -*-
from werkzeug.urls import url_encode

class QueryString(dict):
    """Url query string that supports chaining,
       modifications don't alter the original object."""

    def set_(self, key, val):
        q = QueryString(self)
        q[key] = val
        return q

    def drop(self, key):
        if key in self:
            q = QueryString(self)
            del q[key]
            return q
        return self

    def __str__(self):
        return url_encode(self)
