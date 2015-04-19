Foreword
========

While the purpose for of library is to implement the Pratt parsing algorithm
and to make it more easily accessible. Building real world parsers does and
probably will always require complete understanding of the algorithm involved.

To this end this library should not be understood as a high level abstraction.
Rather Pratt tries to eliminate any overhead required for working at the
abstraction level required.

To this end this documentation will take a bottom up approach. We will take a
look at the theory of how the underlying algorithm works, how it is implemented,
what abstractions are provided on top of it and how these can be used to
effectively parse expressions commonly found in programming languages.
