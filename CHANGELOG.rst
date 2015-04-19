Changelog
=========

Version 0.2.0
-------------

- Added :meth:`pratt.Grammar.enclosing`.
- Changed :class:`pratt.Grammar` by giving it's `__init__` method a default
  implementation for the `handle_unexpected_token` argument. The new default
  implementation raises :exc:`pratt.UnexpectedToken`.
- Added :exc:`pratt.PrattException`. At the moment it's not raised and only
  subclassed by :exc:`pratt.UnexpectedToken`. It's primary reason for existance
  is to serve as a base class for future exceptions.
- Added documentation.
- Added :meth:`pratt.Grammar.ternary`.


Version 0.1.1
-------------

Initial release.
