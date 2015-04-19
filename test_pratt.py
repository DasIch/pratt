# encoding: utf-8
"""
    test_pratt
    ~~~~~~~~~~

    :copyright: 2015 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import re

from pratt import Grammar, Parser

from pytest import raises


def _get_token_type(token):
    return 'integer' if token.isdigit() else token


def _handle_unexpected_token(token):
    assert False, token


def _tokenizer(string):
    return iter(re.findall(r'\+|\-|\*\*|\*|/|\(|\)|\d+', string) + ['EOF'])


def test_handle_unexpected_token_is_called():
    callback_called = [False]
    def handle_unexpected_token(token):
        callback_called[0] = True
        raise ValueError('syntax')
    grammar = Grammar(_get_token_type, handle_unexpected_token)
    parser = Parser(grammar, _tokenizer('1 + 1'))

    with raises(ValueError):
        parser.parse()

    assert callback_called[0]


def test_handle_unexpected_token_not_raising():
    grammar = Grammar(_get_token_type, lambda t: None)
    parser = Parser(grammar, _tokenizer('1 + 1'))

    with raises(RuntimeError):
        parser.parse()


def test_literal():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.literal('integer')
    def l(token):
        return int(token)
    parser = Parser(grammar, _tokenizer('1'))
    result = parser.parse()
    assert result == 1


def test_prefix():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.literal('integer')
    def l(token):
        return int(token)
    @grammar.prefix('-', 10)
    def p(token, operand):
        assert operand == 1
        return -operand
    parser = Parser(grammar, _tokenizer('-1'))
    result = parser.parse()
    assert result == -1


def test_infix():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.literal('integer')
    def l(token):
        return int(token)
    @grammar.infix('+', 10)
    def p(token, left, right):
        return left + right
    parser = Parser(grammar, _tokenizer('1 + 1'))
    result = parser.parse()
    assert result == 2


def test_infix_r():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.literal('integer')
    def l(token):
        return int(token)
    @grammar.infix_r('**', 10)
    def p(token, left, right):
        return left ** right
    parser = Parser(grammar, _tokenizer('2 ** 3 ** 2'))
    result = parser.parse()
    # 2 ** (3 ** 2) == 512 but (2 ** 3) ** 2 == 64
    assert result == 512


def test_postfix():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.literal('integer')
    def l(token):
        return int(token)
    @grammar.postfix('-', 10)
    def p(token, operand):
        assert operand == 1
        return -operand
    parser = Parser(grammar, _tokenizer('1-'))
    result = parser.parse()
    assert result == -1


def test_enclosing():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.literal('integer')
    def integer(token):
        return int(token)
    @grammar.enclosing('(', ')', 100)
    def parentheses(left_paren, right_paren, body):
        assert body == 1
        return body
    parser = Parser(grammar, _tokenizer('(1)'))
    result = parser.parse()
    assert result == 1


def test_null_denotation_is_called_at_expression_start():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    called = [False]
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        called[0] = True
        return 'foo'
    parser = Parser(grammar, iter(['a', 'EOF']))
    result = parser.parse()
    assert result == 'foo'
    assert called[0]


def test_left_denotation_is_called_after_expression_start():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    called = [False]
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        return 'a'
    @grammar.left_denotation('b', 10)
    def left_denotation(token, parser, left):
        assert left == 'a'
        return 'b'
    @grammar.left_denotation('c', 10)
    def left_denotation(token, parser, left):
        assert left == 'b'
        called[0] = True
        return 'c'
    parser = Parser(grammar, iter(['a', 'b', 'c', 'EOF']))
    result = parser.parse()
    assert result == 'c'
    assert called[0]


def test_parse_stops_when_lbp_equal_to_rbp():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        return 'a'
    @grammar.left_denotation('b', 0)
    def left_denotation(token, parser, left):
        return 'b'
    parser = Parser(grammar, iter(['a', 'b', 'EOF']))
    result = parser.parse()
    assert result == 'a'


def test_parse_stops_when_lbp_less_than_rbp():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        return 'a'
    @grammar.left_denotation('b', -1)
    def left_denotation(token, parser, left):
        return 'b'
    parser = Parser(grammar, iter(['a', 'b', 'EOF']))
    result = parser.parse()
    assert result == 'a'


def test_parser_token_ahead_in_null_denotation():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('b')
    grammar.symbol('EOF')
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        assert parser.token == 'b'
        return token
    parser = Parser(grammar, iter(['a', 'b', 'EOF']))
    result = parser.parse()
    assert result == 'a'


def test_parser_token_ahead_in_left_denotation():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('c')
    grammar.symbol('EOF')
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        return token
    @grammar.left_denotation('b', 10)
    def left_denotation(token, parser, left):
        assert parser.token == 'c'
        return token
    parser = Parser(grammar, iter(['a', 'b', 'c', 'EOF']))
    result = parser.parse()
    assert result == 'b'


def test_advance_successful():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        following_token = parser.advance('b')
        assert following_token == 'b'
        return token
    parser = Parser(grammar, iter(['a', 'b', 'EOF']))
    result = parser.parse()
    assert result == 'a'


def test_advance_failure():
    grammar = Grammar(_get_token_type, _handle_unexpected_token)
    grammar.symbol('EOF')
    @grammar.null_denotation('a', 10)
    def null_denotation(token, parser):
        following_token = parser.advance('b')
        assert following_token is None
        return token
    parser = Parser(grammar, iter(['a', 'EOF']))
    result = parser.parse()
    assert result == 'a'
