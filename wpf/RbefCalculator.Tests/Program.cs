using System.Numerics;
using RbefCalculator;

int fails = 0;
void Check(bool ok, string what) { if (!ok) { fails++; Console.WriteLine("FAIL " + what); } }

// 1. Bernoulli numbers 0..200 against sympy (B1 = +1/2 convention)
foreach (var line in File.ReadAllLines("expected_bernoulli.txt"))
{
    var p = line.Split(' ');
    int n = int.Parse(p[0]);
    var exp = new Rat(BigInteger.Parse(p[1]), BigInteger.Parse(p[2]));
    Check(Rbef.Bernoulli(n, true) == exp, $"B_{n}");
}
Console.WriteLine("Bernoulli 0..200 checked");

// 2. generator rows 3..60 against the definition C(m,k)/(k+1)
foreach (var line in File.ReadAllLines("expected_rows.txt"))
{
    var parts = line.Split(' ');
    int m = int.Parse(parts[0]);
    var row = Rbef.GeneratorRow(m);
    Check(row.Length == parts.Length - 1, $"row length m={m}");
    for (int k = 1; k < parts.Length && k <= row.Length; k++)
    {
        var ab = parts[k].Split('/');
        Check(row[k - 1] == new Rat(BigInteger.Parse(ab[0]), BigInteger.Parse(ab[1])), $"A({m},{k})");
    }
}
Console.WriteLine("Generator rows 3..60 checked");

// 3. misc
Check(Rbef.Bernoulli(1, false) == new Rat(-1, 2), "B1 = -1/2");
Check(Rbef.Bernoulli(7, true).IsZero, "B7 = 0");
Check(Rbef.Bernoulli(12, true) == new Rat(-691, 2730), "B12");
Check(Rbef.VonStaudtClausen(100, Rbef.Bernoulli(100, true)) == true, "VSC 100");
Console.WriteLine("B100 = " + Rbef.Bernoulli(100, true));
Console.WriteLine("B100 ~ " + Rbef.Bernoulli(100, true).ToScientific(30));
var sw = System.Diagnostics.Stopwatch.StartNew();
var b600 = Rbef.Bernoulli(600, true);
Console.WriteLine($"B600 computed in {sw.Elapsed.TotalSeconds:F1}s, VSC={Rbef.VonStaudtClausen(600, b600)}");
Console.WriteLine(fails == 0 ? "ALL TESTS PASSED" : $"{fails} FAILURES");
return fails == 0 ? 0 : 1;
