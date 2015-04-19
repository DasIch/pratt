# encoding: utf-8
"""
    pratt
    ~~~~~

    :copyright: 2015 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""


#: The library version as a string.
__version__ = '0.2.0'

#: The library version as a tuple ``(major, minor, patch)``.
__version_info__ = (0, 2, 0)


class PrattException(Exception):
    """
    Base class for exceptions raised by Pratt.
    """


class UnexpectedToken(PrattException):
    """
    Raised when a token is encountered that is not expected at all or not
    expected in the position it was found (null_denotation or left_denotation)
    is missing.
    """
    def __init__(self, token):
        super(UnexpectedToken, self).__init__(token)
        #: The unexpected token.
        self.token = token


def handle_unexpected_token(token):
    """
    Default unexpected token handler that raises :exc:`UnexpectedToken`.
    """
    raise UnexpectedToken(token)


class Grammar(object):
    """
    Grammar objects define the `left_binding_power`, `null_denotation`,
    and `left_denotation` for the tokens in your language.

    :param get_token_type:
        A function that when called with a token, should return a type,
        identifying the token.

    :param handle_unexpected_token:
        A function that gets called when an unexpected token is encountered,
        must raise an exception. The default implementation raises an
        :exc:`UnexpectedToken` error.
    """

    def __init__(self, get_token_type,
                 handle_unexpected_token=handle_unexpected_token):
        self.get_token_type = get_token_type
        self.handle_unexpected_token = handle_unexpected_token
        self._definitions = {}

    def _create_definition(self, type, left_binding_power=0,
                           null_denotation=None, left_denotation=None):
        self._definitions[type] = {
            'left_binding_power': left_binding_power,
            'null_denotation': null_denotation,
            'left_denotation': left_denotation
        }

    def _update_definition(self, type, left_binding_power=0,
                           null_denotation=None, left_denotation=None):
        definition = self._definitions[type]
        definition['left_binding_power'] = max([
            definition['left_binding_power'],
            left_binding_power
        ])
        if null_denotation is not None:
            if definition['null_denotation'] is None:
                definition['null_denotation'] = null_denotation
            else:
                raise RuntimeError('null_denotation already defined')
        if left_denotation is not None:
            if definition['left_denotation'] is None:
                definition['left_denotation'] = left_denotation
            else:
                raise RuntimeError('left_denotation already defined')

    def _create_or_update_definition(self, type, left_binding_power=0,
                                     null_denotation=None,
                                     left_denotation=None):
        if type in self._definitions:
            self._update_definition(
                type, left_binding_power, null_denotation, left_denotation
            )
        else:
            self._create_definition(
                type, left_binding_power, null_denotation, left_denotation
            )

    def symbol(self, type):
        """
        Register a token of the given type.

        Use this to make the grammar aware of tokens, you don't associate
        a `null_denotation` or `left_denotation` with, such as closing
        parenthesis or commas.
        """
        self._create_or_update_definition(type)

    def null_denotation(self, type, left_binding_power=0):
        """
        A decorator that associates the decorated function as `null_denotation`
        for tokens with the given `type`.

        The decorated function will be called with two arguments. The token
        for which the call was triggered and a parser object.

        You can define the `left_binding_power` for this token type, with the
        corresponding argument. If a `left_binding_power` is already defined,
        it chooses the already defined or the given one, depending on which is
        greater.
        """
        def decorate(function):
            self._create_or_update_definition(
                type, null_denotation=function,
                left_binding_power=left_binding_power
            )
            return function
        return decorate

    def left_denotation(self, type, left_binding_power=0):
        """
        A decorator that associates the decorated function as `left_denotation`
        for tokens with the given `type`.

        The decorated function will be called with three arguments. The token
        for which the call was triggered, a parser object and the object
        representing the expression to the left of the token as returned by
        the `null_denotation`/`left_denotation` functions associated with the
        previously found tokens.

        You can define the `left_binding_power` for this token type, with the
        corresponding argument. If a `left_binding_power` is already defined,
        it chooses the already defined or the given one, depending on which is
        greater.
        """
        def decorate(function):
            self._create_or_update_definition(
                type, left_denotation=function,
                left_binding_power=left_binding_power
            )
            return function
        return decorate

    def literal(self, type):
        """
        A decorator for defining literals.

        Creates a `null_denotation` that will call the decorated function with
        a token.
        """
        def decorate(function):
            @self.null_denotation(type)
            def null_denotation(token, parser):
                return function(token)
            return function
        return decorate

    def prefix(self, type, binding_power):
        """
        A decorator for defining prefix operators.

        Creates a `null_denotation` that will call the decorated function with
        the token and operand expression.
        """
        def decorate(function):
            @self.null_denotation(type, binding_power)
            def null_denotation(token, parser):
                operand = parser.parse(right_binding_power=binding_power)
                return function(token, operand)
            return function
        return decorate

    def infix(self, type, binding_power):
        """
        A decorator for defining infix operators.

        Creates a `left_denotation` that will call the decorated function
        with the token, the left, and right operand expressions.
        """
        def decorate(function):
            @self.left_denotation(type, binding_power)
            def left_denotation(token, parser, left):
                right = parser.parse(right_binding_power=binding_power)
                return function(token, left, right)
            return function
        return decorate

    def infix_r(self, type, binding_power):
        """
        A decorator for defining right associative infix operators.

        Creates a `left_denotation` that will call the decorated function
        with the token, the left, and right operand expressions.
        """
        def decorate(function):
            @self.left_denotation(type, binding_power)
            def left_denotation(token, parser, left):
                right = parser.parse(right_binding_power=binding_power - 1)
                return function(token, left, right)
            return function
        return decorate

    def postfix(self, type, binding_power):
        """
        A decorator for defining postfix operators.

        Creates a `left_denotation` that will call the decorated function
        with the token and the operand expression.
        """
        def decorate(function):
            @self.left_denotation(type, binding_power)
            def left_denotation(token, parser, left):
                return function(token, left)
            return function
        return decorate

    def enclosing(self, begin, end, binding_power):
        """
        A decorator for defining expressions that enclose others such as
        parentheses.

        Usage::

            @grammar.enclosing('(', ')', lbp)
            def parentheses(left, right, body):
                return body
        """
        def decorate(function):
            @self.null_denotation(begin, binding_power)
            def null_denotation(left_token, parser):
                body = parser.parse()
                right_token = parser.advance(end)
                return function(left_token, right_token, body)
            self.symbol(end)
            return function
        return decorate

    def ternary(self, first_separator, second_separator, binding_power):
        """
        A decorator for defining ternary operators (such as :? or ..if..else).
        Defines a left denotation for the first seperator.

        Usage::

            @grammar.ternary('if', 'else', 20)
            def if_else(if_token, else_token, then, condition, orelse):
                # do something
                ...
                return result
        """
        def decorate(function):
            @self.left_denotation(first_separator, binding_power)
            def left_denotation(first_sep, parser, first):
                second = parser.parse()
                second_sep = parser.advance(second_separator)
                third = parser.parse()
                return function(first_sep, second_sep, first, second, third)
            self.symbol(second_separator)
            return function
        return decorate


    def _get_definition(self, token):
        type = self.get_token_type(token)
        try:
            return self._definitions[type]
        except KeyError:
            self.handle_unexpected_token(token)
            raise RuntimeError(
                'expected handle_unexpected_token to raise an exception'
            )

    def _get_left_binding_power(self, token):
        definition = self._get_definition(token)
        return definition['left_binding_power']

    def _call_null_denotation(self, token, parser):
        definition = self._get_definition(token)
        if definition['null_denotation'] is None:
            self.handle_unexpected_token(token)
            raise RuntimeError(
                'expected handle_unexpected_token to raise an exception'
            )
        else:
            return definition['null_denotation'](token, parser)

    def _call_left_denotation(self, token, parser, left):
        definition = self._get_definition(token)
        if definition['left_denotation'] is None:
            self.handle_unexpected_token(token)
            raise RuntimeError(
                'expected handle_unexpected_token to raise an exception'
            )
        else:
            return definition['left_denotation'](token, parser, left)


class Parser(object):
    """
    A parser that parses the tokens yielded by a `tokenizer` using the
    given `grammar`.
    """

    def __init__(self, grammar, tokenizer):
        self.grammar = grammar
        self.tokenizer = tokenizer

        #: The token after the one that `null_denotation` or `left_denotation`
        #: has been called for.
        self.token = next(tokenizer)

    def advance(self, type):
        """
        Advances past the next token (:attr:`token`) and returns it, if it has
        the given `type` otherwise remains at the current token and returns
        `None`.
        """
        if self.grammar.get_token_type(self.token) == type:
            advanced = self.token
            self.token = next(self.tokenizer)
            return advanced

    def parse(self, right_binding_power=0):
        """
        Parses and returns an expression until a token with a `left_binding_power`
        greater than or equal to the given `right_binding_power` is reached.
        """
        first = self.token
        self.token = next(self.tokenizer)
        left = self.grammar._call_null_denotation(first, self)
        while right_binding_power < self.grammar._get_left_binding_power(self.token):
            left_token = self.token
            self.token = next(self.tokenizer)
            left = self.grammar._call_left_denotation(left_token, self, left)
        return left
