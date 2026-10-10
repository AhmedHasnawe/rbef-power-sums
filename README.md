# RBEF: power sums of arithmetic sequences

Reference implementation and desktop calculators for the **Recursive Bernoulli
Extraction Formula (RBEF)** described in the paper

> Ahmed Abdlmohsin Abdlsahib, *A Symbolic Differentiation–Summation Framework for
> Power Sums of Arithmetic Sequences.* (arXiv link to be added.)

The paper derives the closed form of

    S_m(n) = sum_{i=1}^{n} (a0 + (i-1) d)^m

by differentiating and integrating the polynomial extension of the sum; the
Bernoulli numbers appear as constants of integration. The formulas are classical;
this repository provides an exact, checkable implementation.

## Contents

| Folder | What it is |
|---|---|
| `python/rbef_reference.py` | Reference code in exact rational arithmetic (the paper's Appendix A) |
| `python/rbef_app.py`, `rbef_logic.py` | Tkinter desktop calculator |
| `wpf/` | C# / WPF desktop calculator (.NET 8) and a console test project |

Both calculators do two things:

1. **Bernoulli number.** Enter the index `n`; get `B_n` as an exact fraction, its
   decimal value, and a von Staudt–Clausen check.
2. **Generator row.** Enter the exponent `m`; get the coefficients
   `A(m,k) = C(m,k)/(k+1)`, `k = 1..m-2`, built from one half by symmetry.

The recurrence yields `C_1 = +1/2` (the value `B_1(1)`); the classical `B_1 = -1/2`
is shown by default and `+1/2` is optional.

## Run

Python 3.8+ (checks need `sympy`):

    python python/rbef_reference.py 300     # runs the seven verification checks
    python python/rbef_app.py               # desktop window (Tkinter)

C#: open `wpf/RbefCalculator.sln` in Visual Studio 2022 (".NET desktop
development"), set `RbefCalculator` as startup project, press F5. The test project
(`wpf/RbefCalculator.Tests`, `dotnet run`) compares `B_0..B_200` with sympy values
and the generator rows `m = 3..60` with the definition.

## Verification status

The Python checks passed for `M = 300`: row = definition = ratio rule; `C_m = B_m`;
odd constants computed (not imposed) and equal to 0; von Staudt–Clausen; closed
form = direct sum; `C_m = d^m B_m(a0/d)`.

## Citation

See `CITATION.cff`. Please also cite the paper once it is public.

## License

MIT, see `LICENSE`.
