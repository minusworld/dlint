#!/usr/bin/env python

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import ast

import unittest

import pytest

import dlint


class TestTree(unittest.TestCase):

    def test_decorator_name_unknown_type(self):
        unknown_type = None

        with pytest.raises(TypeError):
            dlint.tree.decorator_name(unknown_type)


def test_module_path_with_calls():
    code = """
User.query.limit(10).filter_by(id=1)
"""
    tree = ast.parse(code)
    root = tree.body[0].value
    names = dlint.tree.module_path(root)
    assert ["User", "query", "limit", "filter_by"] == names


if __name__ == "__main__":
    unittest.main()
