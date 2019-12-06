import ast
import pytest

import dlint


def run_linter(code):
    tree = ast.parse(code)
    linter = dlint.linters.BadSqlalchemyFilter()
    linter.visit(tree)
    return linter.get_results()


## True positives
def test_bad_filter_limit():
    code = """
@app.route("/get_all_users")
def get_all_users():
    users = User.query.limit(10).filter_by(id=1)
    return users
"""
    assert len(run_linter(code)) == 1


def test_bad_filter_offset():
    code = """
@app.route("/get_all_users")
def get_all_users():
    users = User.query.offset(10).filter_by(id=1)
    return users
"""
    assert len(run_linter(code)) == 1


## True negatives
def test_filter_no_limits():
    code = """
@app.route("/get_users")
def get_users():
    id = request.args.get("id")
    users = User.query.filter_by(id=id).first()
    return users.last_name
"""
    assert len(run_linter(code)) == 0


def test_filter_before_limit():
    code = """
@app.route("/get_users")
def get_users():
    id = request.args.get("id")
    users = User.query.filter_by(name="Joe").limit(10)
    return users.last_name
"""
    assert len(run_linter(code)) == 0


def test_offset_before_limit():
    code = """
@app.route("/get_users")
def get_users():
    id = request.args.get("id")
    users = User.query.filter_by(name="Joe").offset(5)
    return users.last_name
"""
    assert len(run_linter(code)) == 0


def test_from_self_between_limit():
    code = """
@app.route("/get_users")
def get_users():
    id = request.args.get("id")
    users = User.query.limit(10).from_self().filter_by(id=1)
    return users.last_name
"""
    assert len(run_linter(code)) == 0


def test_from_self_between_offset():
    code = """
@app.route("/get_users")
def get_users():
    id = request.args.get("id")
    users = User.query.offset(10).from_self().filter_by(id=1)
    return users.last_name
"""
    assert len(run_linter(code)) == 0


def test_from_self_after():
    code = """
@app.route("/get_users")
def get_users():
    id = request.args.get("id")
    users = User.query.filter_by(id=1).limit(10).from_self()
    return users.last_name
"""
    assert len(run_linter(code)) == 0


def test_filter_by():
    code = """
@app.route("/get_users")
def get_users():
    id = request.args.get("id")
    users = User.query.filter_by(id=id).first()
    return users.last_name
"""
    assert len(run_linter(code)) == 0