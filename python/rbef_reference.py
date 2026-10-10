"""
RBEF reference implementation and verification.

generator_row(m)       : coefficient row A(m,k) = binom(m,k)/(k+1), k=1..m-2,
                         built from one half by A(m,k) = A(m,m-1-k).
rbef_constants(M,a0,d) : constants C_1..C_M by the recurrence of
                         Corollary 4.3. Every constant is computed; the
                         odd-index ones are not skipped, so their
                         vanishing in the normalized case is checked.
verify(M)              : compares with independent references and
                         rebuilds S_m(n) for general a0, d.

Usage: python3 rbef_reference.py [M]   (default M = 300)
Requires Python >= 3.8 (math.comb); the checks need sympy.
"""
import math
import random
import sys
from fractions import Fraction as F


# ------------------------------------------------------ coefficient row
def generator_row(m):
    """[A(m,1), ..., A(m,m-2)], A(m,k) = binom(m+1,k+1)/(m+1)."""
    n = m - 2
    if n < 1:
        return []
    row = [None] * n                  # row[k-1] = A(m,k)
    for k in range(1, n // 2 + 1):    # one half ...
        v = F(math.comb(m + 1, k + 1), m + 1)
        row[k - 1] = v
        row[(m - 1 - k) - 1] = v      # ... and its mirror image
    if n % 2 == 1:                    # a centre exists when m-2 is odd
        k = (n + 1) // 2
        row[k - 1] = F(math.comb(m + 1, k + 1), m + 1)
    assert all(x is not None for x in row)
    return row


# ------------------------------------------------------ RBEF constants
def rbef_constants(M, a0=F(1), d=F(1)):
    a0, d = F(a0), F(d)
    C = {1: a0 - d / 2}
    for m in range(2, M + 1):
        row = generator_row(m)
        s = F(0)
        for k in range(1, m - 1):
            s += row[k - 1] * d ** (m - k - 1) * C[k + 1]
        C[m] = a0 ** m - d ** m / (m + 1) - d ** (m - 1) * C[1] - s
    return C


def power_sum_from_rbef(m, n, a0, d, C):
    a0, d, n = F(a0), F(d), F(n)
    tot = d ** m * n ** (m + 1) / (m + 1) + d ** (m - 1) * C[1] * n ** m
    row = generator_row(m)
    for k in range(1, m - 1):
        tot += row[k - 1] * d ** (m - k - 1) * C[k + 1] * n ** (m - k)
    if m >= 2:
        tot += C[m] * n               # the k = m-1 term, A(m,m-1) = 1
    return tot


def direct_power_sum(m, n, a0, d):
    return sum((F(a0) + F(d) * (i - 1)) ** m for i in range(1, n + 1))


# ------------------------------------------------------ verification
def _primes_upto(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i, v in enumerate(sieve) if v]


def _frac(r):
    """sympy Rational -> Fraction"""
    return F(int(r.p), int(r.q))


def verify(M=300, seed=1):
    import sympy as sp
    ok_all = True

    def report(name, ok, extra=""):
        nonlocal ok_all
        ok_all &= bool(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {extra}")

    # 1. row versus the definition binom(m,k)/(k+1) and the ratio rule
    bad = []
    for m in range(3, M + 1):
        defn = [F(math.comb(m, k), k + 1) for k in range(1, m - 1)]
        ratio = [F(m, 2)]
        for k in range(1, m - 2):
            ratio.append(ratio[-1] * F(m - k, k + 2))
        if not (generator_row(m) == defn == ratio):
            bad.append(m)
    report("row = binom(m,k)/(k+1) = ratio rule", not bad,
           f"(m=3..{M}; bad: {bad[:5]})")

    # 2. normalized constants versus Bernoulli numbers
    C = rbef_constants(M)
    wrong = [m for m in range(2, M + 1)
             if C[m] != _frac(sp.bernoulli(m))]
    report("C_m = B_m, 2<=m<=M", not wrong, f"(M={M}; bad: {wrong[:5]})")
    report("C_1 = a0 - d/2 = +1/2 (by construction)", C[1] == F(1, 2))

    # 3. odd constants vanish although nothing forces them to
    odd = [m for m in range(3, M + 1, 2) if C[m] != 0]
    report("odd C_m = 0 (computed)", not odd,
           f"({len(range(3, M + 1, 2))} values)")

    # 4. von Staudt-Clausen
    vsc_bad = []
    for m in range(2, M + 1, 2):
        ps = [p for p in _primes_upto(m + 1) if m % (p - 1) == 0]
        if (C[m] + sum(F(1, p) for p in ps)).denominator != 1:
            vsc_bad.append(m)
    report("von Staudt-Clausen", not vsc_bad)

    # 5. closed form versus direct sums for general a0, d
    rng = random.Random(seed)
    Mp = min(M, 40)
    bad_ps = 0
    for _ in range(25):
        a0 = F(rng.randint(-9, 9), rng.randint(1, 5))
        d = F(rng.choice([x for x in range(-7, 8) if x]),
              rng.randint(1, 4))
        Cg = rbef_constants(Mp, a0, d)
        for m in range(1, Mp + 1):
            for n in range(1, m + 3):     # m+2 points fix the polynomial
                if (power_sum_from_rbef(m, n, a0, d, Cg)
                        != direct_power_sum(m, n, a0, d)):
                    bad_ps += 1
    report("closed form = direct sum", bad_ps == 0,
           f"(25 pairs, m=1..{Mp}, n=1..m+2; failures: {bad_ps})")

    # 6. C_m(a0,d) = d^m B_m(a0/d)
    x = sp.Symbol("x")
    rel_bad = 0
    for _ in range(6):
        a0 = F(rng.randint(1, 9), rng.randint(1, 4))
        d = F(rng.randint(1, 7), rng.randint(1, 3))
        Cg = rbef_constants(25, a0, d)
        y = sp.Rational(a0.numerator, a0.denominator) / \
            sp.Rational(d.numerator, d.denominator)
        dd = sp.Rational(d.numerator, d.denominator)
        for m in range(2, 26):
            if Cg[m] != _frac(dd ** m * sp.bernoulli(m, x).subs(x, y)):
                rel_bad += 1
    report("C_m = d^m B_m(a0/d)", rel_bad == 0, f"(failures: {rel_bad})")

    print("\nOVERALL:", "all checks passed" if ok_all else "FAILURES")
    return ok_all


if __name__ == "__main__":
    verify(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
