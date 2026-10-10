using System.Numerics;
using System.Text;

namespace RbefCalculator;

/// <summary>Exact rational number (normalised, denominator &gt; 0).</summary>
public readonly struct Rat : IEquatable<Rat>
{
    public BigInteger Num { get; }
    public BigInteger Den { get; }

    public Rat(BigInteger num, BigInteger den)
    {
        if (den.IsZero) throw new DivideByZeroException();
        if (den.Sign < 0) { num = -num; den = -den; }
        var g = BigInteger.GreatestCommonDivisor(num, den);
        if (!g.IsZero && !g.IsOne) { num /= g; den /= g; }
        if (num.IsZero) den = BigInteger.One;
        Num = num; Den = den;
    }

    public static Rat FromInt(BigInteger n) => new(n, BigInteger.One);
    public static readonly Rat Zero = FromInt(0);
    public static readonly Rat One = FromInt(1);

    public bool IsZero => Num.IsZero;
    public bool IsInteger => Den.IsOne;

    public static Rat operator +(Rat a, Rat b) => new(a.Num * b.Den + b.Num * a.Den, a.Den * b.Den);
    public static Rat operator -(Rat a, Rat b) => new(a.Num * b.Den - b.Num * a.Den, a.Den * b.Den);
    public static Rat operator *(Rat a, Rat b) => new(a.Num * b.Num, a.Den * b.Den);
    public static Rat operator /(Rat a, Rat b) => new(a.Num * b.Den, a.Den * b.Num);
    public static Rat operator -(Rat a) => new(-a.Num, a.Den);

    public bool Equals(Rat o) => Num == o.Num && Den == o.Den;
    public override bool Equals(object? obj) => obj is Rat r && Equals(r);
    public override int GetHashCode() => HashCode.Combine(Num, Den);
    public static bool operator ==(Rat a, Rat b) => a.Equals(b);
    public static bool operator !=(Rat a, Rat b) => !a.Equals(b);

    public override string ToString() => IsInteger ? Num.ToString() : $"{Num}/{Den}";

    /// <summary>Scientific notation with the given number of significant digits (truncated).</summary>
    public string ToScientific(int digits = 30)
    {
        if (Num.IsZero) return "0";
        var a = BigInteger.Abs(Num);
        int s = digits + Den.ToString().Length - a.ToString().Length + 1;
        BigInteger q = s >= 0 ? a * BigInteger.Pow(10, s) / Den
                              : a / (Den * BigInteger.Pow(10, -s));
        string qs = q.ToString();
        int exp = qs.Length - 1 - s;
        string mant = qs.Substring(0, Math.Min(digits, qs.Length));
        var sb = new StringBuilder();
        if (Num.Sign < 0) sb.Append('-');
        sb.Append(mant[0]);
        if (mant.Length > 1) sb.Append('.').Append(mant, 1, mant.Length - 1);
        if (exp != 0) sb.Append('e').Append(exp > 0 ? "+" : "-").Append(Math.Abs(exp));
        return sb.ToString();
    }
}

/// <summary>RBEF computations (a0 = d = 1), mirroring the verified Python reference.</summary>
public static class Rbef
{
    public const int MaxN = 1000;
    public const int MaxM = 5000;

    /// <summary>
    /// Coefficient row A(m,k) = C(m,k)/(k+1) = C(m+1,k+1)/(m+1), k = 1..m-2.
    /// One half is computed and mirrored: A(m,k) = A(m,m-1-k).
    /// Index k-1 holds A(m,k). Empty for m &lt; 3.
    /// </summary>
    public static Rat[] GeneratorRow(int m)
    {
        int n = m - 2;
        if (n < 1) return Array.Empty<Rat>();
        var row = new Rat[n];
        var mp1 = new BigInteger(m + 1);
        // binom(m+1, j+1) with j = k+1 ... start at k = 1: binom(m+1, 2)
        BigInteger b = new BigInteger(m + 1) * m / 2;      // binom(m+1,2)
        int half = n % 2 == 1 ? (n + 1) / 2 : n / 2;       // include the centre when it exists
        for (int k = 1; k <= half; k++)
        {
            var v = new Rat(b, mp1);
            row[k - 1] = v;
            row[(m - 1 - k) - 1] = v;
            // binom(m+1, k+2) = binom(m+1, k+1) * (m+1-(k+1)) / (k+2)
            b = b * (m - k) / (k + 2);
        }
        return row;
    }

    /// <summary>Constants C_1..C_M by the recurrence of Corollary 4.3 (a0 = d = 1). C[0] = 1.</summary>
    public static Rat[] Constants(int M)
    {
        var C = new Rat[Math.Max(M, 1) + 1];
        C[0] = Rat.One;
        C[1] = new Rat(1, 2);
        for (int m = 2; m <= M; m++)
        {
            var row = GeneratorRow(m);
            var s = Rat.Zero;
            for (int k = 1; k <= m - 2; k++)
                s += row[k - 1] * C[k + 1];
            C[m] = Rat.One - new Rat(1, m + 1) - C[1] - s;
        }
        return C;
    }

    private static Rat[] _cache = Array.Empty<Rat>();
    private static readonly object _lock = new();

    /// <summary>B_n via the RBEF recurrence. The recurrence gives C_1 = +1/2;
    /// with plusOneHalf = false, B_1 = -1/2 is returned.</summary>
    public static Rat Bernoulli(int n, bool plusOneHalf)
    {
        if (n == 0) return Rat.One;
        lock (_lock)
        {
            if (_cache.Length <= n) _cache = Constants(n);
            var v = _cache[n];
            return n == 1 && !plusOneHalf ? -v : v;
        }
    }

    /// <summary>Even n &gt;= 2: B_n + sum over primes p with (p-1)|n of 1/p must be an integer.</summary>
    public static bool? VonStaudtClausen(int n, Rat value)
    {
        if (n < 2 || n % 2 != 0) return null;
        var s = Rat.Zero;
        for (int p = 2; p <= n + 1; p++)
            if (n % (p - 1) == 0 && IsPrime(p))
                s += new Rat(1, p);
        return (value + s).IsInteger;
    }

    private static bool IsPrime(int p)
    {
        if (p < 2) return false;
        for (int q = 2; (long)q * q <= p; q++) if (p % q == 0) return false;
        return true;
    }
}
