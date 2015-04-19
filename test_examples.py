# encoding: utf-8
"""
    test_examples
    ~~~~~~~~~~~~~

    :copyright: 2015 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'examples'))
import math_expr


class TestMath(object):
    """
    Tests for the `examples/math_expr.py` module.
    """
    def test_addition(self):
        assert math_expr.evaluate('1 + 1') == 2

    def test_subtraction(self):
        assert math_expr.evaluate('1 - 1') == 0

    def test_multiplication(self):
        assert math_expr.evaluate('2 * 2') == 4

    def test_division(self):
        assert math_expr.evaluate('4 / 2') == 2

    def test_parentheses(self):
        assert math_expr.evaluate('(1 + 1) * 2') == 4

    def test_multiplication_before_addition(self):
        assert math_expr.evaluate('1 + 1 * 2') == 3

    def test_multiplication_before_subtraction(self):
        assert math_expr.evaluate('2 - 1 * 2') == 0

    def test_division_before_addition(self):
        assert math_expr.evaluate('2 + 4 / 2') == 4

    def test_division_before_subtraction(self):
        assert math_expr.evaluate('2 - 4 / 2') == 0
