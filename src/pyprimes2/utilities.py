# -*- coding: utf-8 -*-

##  Part of the pyprimes.py package.
##
##  Copyright © 2014 Steven D'Aprano.
##  See the file __init__.py for the licence terms for this software.

from __future__ import division


# Every integer between 0 and MAX_EXACT inclusive
MAX_EXACT = 9007199254740991


# Get the number of bits needed to represent an int in binary.
try:
    _bit_length = int.bit_length
except AttributeError:
    def _bit_length(n):
        if n == 0:
            return 0
        elif n < 0:
            n = -n
        assert n >= 1
        numbits = 0
        # Accelerator for larger values of n.
        while n > 2**64:
            numbits += 64; n >>= 64
        while n:
            numbits += 1; n >>= 1
        return numbits


def isqrt(n):
    """Return the integer square root of n.

    >>> isqrt(48)
    6
    >>> isqrt(49)
    7
    >>> isqrt(9500)
    97

    Equivalent to floor(sqrt(x)).
    """
    if n < 0:
        raise ValueError('square root not defined for negative numbers')
    elif n <= MAX_EXACT:
        # For speed, we use floating point maths.
        return int(n**0.5)
    return _isqrt(n)

def _isqrt(n):
    # Tested every value of n in the following ranges:
    #   - range(0, 9394201554) (took about ~12.5 hours)
    #   - range(9007154720172961, 9007154885883381)
    #
    if n == 0:
        return 0
    bits = _bit_length(n)
    a, b = divmod(bits, 2)
    x = 2**(a+b)
    while True:
        y = (x + n//x)//2
        if y >= x:
            return x
        x = y


# === Instrumentation used by the probabilistic module ===


try:
    from collections import namedtuple
except ImportError:
    # Probably Python 2.4. If namedtuple is not available, just use a
    # regular tuple instead.
    def namedtuple(name, fields):
        return tuple


class PerMethodInstrument(object):
    """Instrumentation for individual sub-methods of ``is_probably_prime``.

    Instances are intended to be mapped to a method name in a dict, where
    they record how often the method was able to conclusively determine
    the primality of its argument (that is, by returning 0 or 1 rather
    than 2).

    Instances record three pieces of data:

        hits:
            The number of times the method conclusively determined
            the primality of the argument.

        low:
            The smallest argument that the method has determined
            the primality of the argument.

        high:
            The largest argument that the method has determined
            the primality of the argument.

    E.g. given a mapping ``{"frob": PerMethodInstrument(250, 357, 993)}``,
    that indicates that the method ``frob`` determined the primality of its
    argument 250 times (not necessarily distinct arguments), with the
    smallest such argument being 357 and the largest being 993.

    """
    def __init__(self, hits=0, low=None, high=None):
        self.hits = hits
        self.low = low
        self.high = high

    def __repr__(self):
        template = "%s(hits=%d, low=%r, high=%r)"
        name = type(self).__name__
        return template % (name, self.hits, self.low, self.high)

    def update(self, value):
        self.hits += 1
        a, b = self.min, self.max
        if a is None: a = value
        else: a = min(a, value)
        if b is None: b = value
        else: b = max(b, value)
        self.min, self.max = a, b


class Instrument(object):
    """Instrumentation for ``is_probable_prime``.

    Instrument objects have four public attributes recording total counts:

        calls:
            The total number of times the function is successfully called.

        not_prime:
            The total number of non-prime results returned.

        prime:
            The total number of definitely prime results returned.

        uncertain:
            The total number of possibly prime results returned.




    """
    def __init__(self, methods):
        self.calls = 0
        self.uncertain = 0
        self._data = {}
        self.instrument = {'calls': 0, 'uncertain': 0}
        for method in self._methods:
            self.instrument[method] = (0, None, 0)  # hits, min, max

    def __str__(self):
        template = "[[ calls: %d; uncertain: %d ]\n %s]"
        items = sorted(self._data.items())
        items = ['[ %s: %s ]' % item for item in items]
        items = '\n '.join(items)
        return template % (self.calls, self.uncertain, items)
