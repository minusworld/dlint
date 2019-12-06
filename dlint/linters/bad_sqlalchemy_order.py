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
    try:
        return sequence.index(item)
    except ValueError:
        return -1


class BadSqlalchemyFilter(base.BaseLinter):
    """Checks for SQLAlchemy filter() occurring after limit() or offset(). This scenario will
    raise a runtime error. To fix, do filter() before the others, or call from_self() after
    the limit() or offset() call. E.g., Model.query.limit(100).from_self().filter_by(cond=val)
    """

    _code = "DUO138"
    _error_tmpl = "DUO138 applying SQLAlchemy methods out of order will cause a runtime exception."


    sqlalchemy_filter_methods = {"filter", "filter_by"}
    sqlalchemy_limit_methods = {"limit", "offset"}
    sqlalchemy_from_self = "from_self"

    sqlalchemy_bad_update_delete_left_side = {            
        "limit",
        "offset",
        "order_by",
        "group_by",
        "distinct",
        "join",
        "outerjoin",
        "select_from",
        "from_self"
    }
    sqlalchemy_update_delete = {
        "update",
        "delete"
    }


    def _filter_after_limit(self, node):
        if node.attr in self.sqlalchemy_filter_methods:
            attr_sequence = tree.module_path(node)
            filter_index = _index(attr_sequence, node.attr)
            limit_index = max([_index(attr_sequence, m) for m in self.sqlalchemy_limit_methods])
            if limit_index >= 0 and limit_index < filter_index:
                from_self_index = _index(attr_sequence, self.sqlalchemy_from_self)
                if not (limit_index < from_self_index and from_self_index < filter_index):
                    return True
        return False


    def _bad_update_or_delete(self, node):
        if node.attr in self.sqlalchemy_update_delete:
            attr_sequence = tree.module_path(node)
            greatest_bad_left_index = max([_index(attr_sequence, m) for m in self.sqlalchemy_bad_update_delete_left_side])
            if greatest_bad_left_index < 0:
                return False
            update_delete_index = _index(attr_sequence, node.attr)
            if greatest_bad_left_index < update_delete_index: # If update/delete comes after the others
                return True
        return False


    def visit_Attribute(self, node):
        hit = False
        if self._filter_after_limit(node):
            hit = True 
        elif self._bad_update_or_delete(node):
            hit = True

        if hit:
            self.results.append(
                base.Flake8Result(
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    message=self._error_tmpl
                )
            )
