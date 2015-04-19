Tutorial Step 1: Algorithm
==========================

The algorithm behind the parser is very simple. For each type of token there
exists a

left binding power
        An integer greater than 0.

null denotation
        A function that is called with the parser and the token for which it
        was defined. It's supposed to return a result, usually something like
        an abstract syntax tree node.

left denotation
        A function that should behave like the null denotation function but
        takes as an additional argument an intermediate result as returned by
        a null denotation or left denotation function.

The parser itself is called with a sequence of tokens and a *right binding
power*. It takes the first token from the sequence and calls the null
denotation function for it, producing an intermediate result. After that it
iterates through the remaining tokens, calling their left denotations until
a token is reached whose left binding power is less than or equal to the
right binding power. After that the result is returned.

Let's try to understand what actions this allows us. Based on the algorithm
itself an expression is required to consist of at least one token and if an
expression consists of only one token, it's null denotation is called. That
means parsing string, numbers, and other such objects requires using a null
denotation.

Another thing we might want to do is parse operators. Using a null denotation
we can easily parse prefix operators by recursively calling the parser. Parsing
infix operators is more difficult. We want to stop parsing at the operator
token, that means assigning a higher left binding power to such tokens than to
numbers etc. in addition that means we need a left denotation for such
operators. The parser stopping however, requires that we use recursion to get
the right operand.

Operator precedence can be easily dealt with, by defining operators with higher
precedence, to have a higher left binding power than those with lower
precedence.

Now that we have explored the algorithm somewhat, let's take a look at how we
can create such parsers using this library in :doc:`tutorial-step-2-implementation`.
