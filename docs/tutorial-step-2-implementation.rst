Tutorial Step 2: Implementation
===============================

Now that you are familiar with the algorithm, let's take a look at how we can
create parsers using it.

Pratt defines two classes you will interact with :class:`pratt.Grammar` and
:class:`pratt.Parser`. :class:`~pratt.Grammar` is used to provide Pratt with
the necessary information about how to deal with tokens and more importantly to
define the mapping of token types to their null and left denotations.
:class:`Parser` is used to parse a particular sequence of tokens, using a
grammar you defined.

In this tutorial we are going to parse mathematical expressions. This is a
common task and allows us to easily cover everything you need to know. Given
that Pratt doesn't provide any tools for tokenization we have to come up with
our own. For the purposes of this tutorial, this will be our tokenizer::

        import re


        token_re = re.compile(r"""
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
                for type, lexeme in match.groupdict().items():
                    if lexeme is None or type == 'whitespace':
                        continue
                    yield type, lexeme
                    break
            yield 'end', ''

We don't want to focus on tokenization, so we won't go into how it works. Let's
continue by creating a grammar instance to work with::

        from operator import itemgetter

        from pratt import Grammar


        grammar = Grammar(itemgetter(0))

In order to map not just token types but tokens to what's defined in the
grammar, we need to give the grammar a function that takes a token and returns
it's type. In our case tokens are tuples, consisting of a type and a lexeme. So
we can simply pass an :func:`~operator.itemgetter` to the parser for that.

We can now use this grammar with a :class:`~pratt.Parser` and our tokenize
function. For convenience let's create ourselves a function that uses both to
parse an expression in source form::

        from pratt import Parser

        def parse(source):
            tokens = tokenize(source)
            parser = Parser(grammar, tokens)
            return parser.parse()

We could now use this to parse expressions for example ``parse('1 + 1')``.
However this would raise a :exc:`pratt.UnexpectedToken` exception as our
grammar is empty at the moment. Let's change that. In the last step the first
thing we considered parsing where things like strings or numbers. In our case
we have only one such thing `int`. So let's parse it with a null denotation::


        @grammar.null_denotation('int')
        def parse_int(token, parser):
            return int(token[1])


As you can see we use :meth:`~pratt.Grammar.null_denotation` as a decorator to
define a null denotation for the `int` token type. While we could define a left
binding power, Pratt assumes one of 0 by default which is sufficient in this
case. As a result we are simply going to convert the integer into a Python
:func:`int`.

Now with at least a null denotation for integer defined, we can actually use
`parse` and get a useful result:

>>> parse('1')
1

We don't just want to parse single integer though, we also want to define
operators on them. Let's begin with addition::

        @grammar.left_denotation('add', 10)
        def parse_add(token, parser, left_operand):
            # Continue parsing until a token of equal or lesser left binding
            # power is encountered.
            right_operand = parser.parse(right_binding_power=10)
            return left_operand + right_operand

Just like null denotations, left denotations are defined with a decorator
:meth:`~pratt.Grammar.left_denotation`. In this case we do explicitly define a
left binding power, as we want one that's greater than 0. Simply choosing 1
would have done the job but especially during early development it's convenient
to use multiples of 10. This gives you some space inbetween token's left
binding powers, so that you don't have to shift them all around for small
changes.

Usually you would want to return some kind of abstract syntax tree node in the
`parse_add` function but I don't want to go into defining AST classes here, so
our parser will simply return the result of calculating the expression.

Again we can test that this works by playing around with the `parse` function:

>>> parse('1 + 1')
2
>>> parse('1 + 1 + 1')
3

Now let's add another operator, this time one with higher precedence::

        @grammar.left_denotation('mul', 20)
        def parse_mul(token, parser, left_operand):
            right_operand = parser.parse(20)
            return left_operand * right_operand

As you can see this mirrors the definition of `parse_add`. There is nothing
surprising here and this cost us little effort. Let's try it to see, if it works:

>>> parse('2 * 2')
4
>>> parse('1 + 1 * 2')
3

Now that you have seen how it works, you should try to implement the remaining
parts on your own.

Looking the code, you may notice some repetition. That repetition looks bad and
as you may already know is generally a bad thing. Let's take a look at how to
avoid this repetition in :doc:`tutorial-step-3-abstraction`.
