#!/usr/bin/env python

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import ast

from . import base
from .. import tree


def _index(sequence, item):
    return sequence.index(item) if item in sequence else -1


class BadSqlalchemyFilter(base.BaseLinter):
    """Checks for SQLAlchemy filter() occurring after limit() or offset(). This scenario will
    raise a runtime error. To fix, do filter() before the others, or call from_self() after
    the limit() or offset() call. E.g., Model.query.limit(100).from_self().filter_by(cond=val)
    """

    _code = "DUO138"
    _error_tmpl = f"{_code} applying filter() after limit() or offset() without a from_self() in between will raise a runtime error."
    _long_error_tmpl = f"{_code} Query.filter() being called on a Query which already has LIMIT or OFFSET applied. This will raise a runtime error. To modify the row-limited results of a  Query, call from_self() first.  Otherwise, call filter() before limit() or offset() are applied."


    sqlalchemy_filter_methods = {"filter", "filter_by"}
    sqlalchemy_limit_methods = {"limit", "offset"}
    sqlalchemy_from_self = "from_self"


    def visit_Attribute(self, node):
        if node.attr in self.sqlalchemy_filter_methods:
            attr_sequence = tree.module_path(node)
            filter_index = _index(attr_sequence, node.attr)
            limit_index = min([_index(attr_sequence, m) for m in self.sqlalchemy_limit_methods])
            if limit_index < filter_index:
                from_self_index = _index(attr_sequence, self.sqlalchemy_from_self)
                if not (limit_index < from_self_index and from_self_index < filter_index):
                    self.results.append(
                        base.Flake8Result(
                            lineno=node.lineno,
                            col_offset=node.col_offset,
                            message=self._error_tmpl
                        )
                    )