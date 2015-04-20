Pratt
=====

Pratt is a Python library for creating Pratt parsers. Pratt parsers are
recursive descent operator precedence parsers. Such parsers are well suited
to parsing expressions and integrate well into regular recursive descent
parsers.

A minimal parser using Pratt looks like this::

        from pratt import Grammar, Parser

        def get_token_type(token):
            return token[0]

        def handle_unexpected_token(token):
            # Custom exception type omitted for brevity
            raise SyntaxErrror('oops: {!r}'.format(token))

        grammar = Grammar(get_token_type=lambda token: token[0]
        grammar.symbol('end')

        @grammar.literal('int')
        def handle_int(token):
            return int(token[1])

        @grammar.infix('+', 10)
        def add(token, left, right):
            return left + right


        tokens = [('int', 1), ('+', '+'), ('int', 1)]
        parser = Parser(grammar, tokens)
        result = parser.parse()
        print(result)
        # 2

A more realistic and well commented example for parsing mathematical expressions,
is `examples/math_expr.py`, in the Pratt source code repository.

As you can see Pratt itself provides no utilities for tokenization. Doing so
in a way that satifies everyones needs is fairly complex and therefore out
of scope for this project. On the other hand Pratt makes no assumptions about
your tokens, allowing easy integration with whatever solution you want to use
for that purpose.

Pratt is licensed under the 3-clause BSD license.
