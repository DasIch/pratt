Tutorial Step 3: Abstraction
============================

Now that you know the low-level basics of Pratt. Let's take a look at which
abstractions it provides to avoid repetition.

While in this tutorial we are looking at mathematical expressions that only use
integers. Parsing literals is still a fairly common occurance, this is why
:meth:`~pratt.Grammar.literal` exists::

        @grammar.literal('int', 1)
        def parse_int(token):
            return int(token[1])

This decorator cuts through some of the overhead of
:meth:`~pratt.Grammar.null_denotation` and makes your intent more obvious.

Apart from literals another thing you are probably going to parse fairly often
are operators. For this reason a series of decorators exist that makes it easy
to define different types of operators::

        @grammar.prefix('add', 100)
        def prefix_add(token, operand):
            return +operand

        @grammar.infix('add', 10)
        def infix_add(token, left, right):
            return left + right

        @grammar.infix_r('pow', 40)
        def pow(token, left, right):
            return left ** right

        @grammar.postfix('bang')
        def factorial(token, operand):
            if operand == 0:
                return 1
            return reduce(mul, range(1, operand + 1))

With that you know (almost) everything there is to know about Pratt. Go forth
and parse things.
