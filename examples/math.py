# encoding: utf-8
"""
    math
    ~~~~

    This is an example for a parser that parses and evaluates mathematical
    expressions.

    :copyright: 2015 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import re
import sys
from operator import itemgetter

from pratt import Grammar, Parser


token_re = re.compile(ur"""
    (?P<int>\d+)|
    (?P<add>\+)|
    (?P<sub>-)|
    (?P<mul>\*)|
    (?P<div>/)|
    (?P<left_paren>\()|
    (?P<right_paren>\))|
    (?P<whitespace>\s+)
""", re.VERBOSE)


def tokenize(string):
    """
    This returns an iterator yielding tuples consisting of a type and a lexeme.

    Possible types are `int`, `add`, `sub`, `mul`, `div`, `left_paren`,
    `right_paren` and `end`. Lexemes are always strings.
    """
    for match in token_re.finditer(string):
        for type, lexeme in match.groupdict().iteritems():
            if lexeme is None or type == 'whitespace':
                continue
            yield type, lexeme
            break
    yield 'end', ''


class SyntaxError(Exception):
    pass


def handle_unexpected_token(token):
    """
    Called when the parser encounters a token it doesn't know about.
    """
    raise SyntaxError('unexpected token: {!r}'.format(token[0]))


grammar = Grammar(itemgetter(0), handle_unexpected_token)

# The end token exists only as an indicator, we are not using it anywhere and
# are therefore not associating it with anything. Nevertheless we have to tell
# the parser that it's a token that exists and might appear.
grammar.symbol('end')


@grammar.literal('int')
def handle_int(token):
    # We evaluate the mathematical expression as part of the parsing process,
    # therefore we simply turn the lexeme (remember, that's the second element in
    # the tuple) into a Python int.
    #
    # In the "real world" we would probably want our parser to return an AST,
    # that can be inspected instead.
    return int(token[1])


@grammar.prefix('add', 100)
def prefix_add(token, operand):
    # Called when + is used as a prefix operator. `operand` is something that
    # was returned by one of our parsing functions.
    #
    # We define this operator to have a left binding power of 100 because we
    # want it to bind more tightly than infix operators and we don't want to
    # bother carefully considering how much "space" we need below that for
    # other operators.
    return +operand


@grammar.prefix('sub', 100)
def prefix_sub(token, operand):
    return -operand


@grammar.infix('add', 10)
def infix_add(token, left, right):
    # This function implements the addition operator. We define addition to
    # have a left binding power of 10.
    #
    # The default binding power is 0, so we could have gone with 1 as well but
    # using a larger one allows us to potentially squeeze in something else at
    # a later date without having to change binding powers everywhere.
    return left + right


@grammar.infix('sub', 10)
def infix_sub(token, left, right):
    return left - right


@grammar.infix('mul', 20)
def infix_mul(token, left, right):
    # This is almost the same as our addition and subtraction operators. The
    # only really difference is that the left binding power is higher at 20.
    # This tells the parser that multiplication binds more tightly, so that
    # 1 + 1 * 2 is evaluated to 3 as opposed to 4.
    return left * right


@grammar.infix('div', 20)
def infix_div(token, left, right):
    return left // right


@grammar.null_denotation('left_paren')
def parenthesis(token, parser):
    # Mathematical expressions would be useless without parenthesis. Here
    # we define a null denotation with a left binding power of 0. This will
    # be called as soon as the parser encounters it, we then call the parser
    # again recursively and skip past the closing parenthesis.
    expression = parser.parse()
    parser.advance('right_paren')
    return expression

# Similar to the end token we made the parser aware of in the beginning, we
# have to do the same for the right or closing parenthesis.
grammar.symbol('right_paren')


def evaluate(string):
    """
    Evaluates a mathematical expressions. Available operators are `+`, `-`, `*`
    and `/`. Parenthesis are supported. The only available numbers are
    integers. Whitespace is ignored.
    """
    tokenizer = tokenize(string)
    parser = Parser(grammar, tokenizer)
    return parser.parse()


if __name__ == '__main__':
    expression = ' '.join(sys.argv[1:])
    print '> {}'.format(expression)
    print evaluate(expression)
