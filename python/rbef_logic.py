"""Pure logic of the RBEF Calculator (no GUI), built on rbef_reference.py."""
from decimal import Decimal, getcontext
from fractions import Fraction as F

from rbef_reference import generator_row, rbef_constants

MAX_N = 600          # keep the recurrence responsive (cost grows like n^2)
MAX_M = 3000


# ----------------------------------------------------------------- logic
_cache = {"M": 0, "C": {}}


def bernoulli(n, plus_one_half=True):
    """B_n from the RBEF recurrence (a0 = d = 1). Returns a Fraction.

    The recurrence yields C_1 = +1/2 (the value B_1(1)). With
    plus_one_half=False the classical convention B_1 = -1/2 is returned.
    """
    if n == 0:
        return F(1)
    if n > _cache["M"]:
        _cache["C"] = rbef_constants(max(n, 1))
        _cache["M"] = max(n, 1)
    v = _cache["C"][n]
    if n == 1 and not plus_one_half:
        v = -v
    return v


def to_decimal(fr, digits=30):
    getcontext().prec = digits
    if fr == 0:
        return "0"
    return format(Decimal(fr.numerator) / Decimal(fr.denominator), ".%dg" % digits)


def von_staudt_ok(n, val):
    """Even n >= 2: B_n + sum_{(p-1)|n} 1/p must be an integer."""
    if n < 2 or n % 2:
        return None
    s = F(0)
    for p in range(2, n + 2):
        if n % (p - 1) == 0 and all(p % q for q in range(2, int(p ** 0.5) + 1)):
            s += F(1, p)
    return (val + s).denominator == 1


def generator_values(m):
    """[(k, A(m,k))] for k = 1..m-2, plus the extra k = m-1 entry (=1)."""
    row = generator_row(m)
    out = [(k, row[k - 1]) for k in range(1, m - 1)]
    return out
