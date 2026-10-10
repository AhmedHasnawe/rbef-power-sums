using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Input;
using Microsoft.Win32;

namespace RbefCalculator;

public partial class MainWindow : Window
{
    public MainWindow() => InitializeComponent();

    // ------------------------------------------------------------ Bernoulli
    private void TxtN_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter) BtnBernoulli_Click(sender, e);
    }

    private async void BtnBernoulli_Click(object sender, RoutedEventArgs e)
    {
        if (!int.TryParse(TxtN.Text.Trim(), out int n) || n < 0 || n > Rbef.MaxN)
        {
            MessageBox.Show($"n يجب أن يكون عددًا صحيحًا بين 0 و {Rbef.MaxN}.", "إدخال غير صالح");
            return;
        }
        bool plus = ChkPlus.IsChecked == true;
        BtnBernoulli.IsEnabled = false;
        Status1.Text = $"جارٍ حساب B_{n} ...";
        try
        {
            var v = await Task.Run(() => Rbef.Bernoulli(n, plus));
            Out1.Text = DescribeBernoulli(n, v, plus);
            Status1.Text = "تم.";
        }
        catch (Exception ex)
        {
            MessageBox.Show(ex.Message, "خطأ");
            Status1.Text = "فشل الحساب.";
        }
        finally { BtnBernoulli.IsEnabled = true; }
    }

    private static string DescribeBernoulli(int n, Rat v, bool plus)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"B_{n}  (RBEF recurrence, a0 = d = 1)");
        sb.AppendLine();
        if (n == 1)
        {
            sb.AppendLine($"convention: B1 = {(plus ? "+1/2" : "-1/2")}");
            sb.AppendLine();
        }
        sb.AppendLine("Exact value:");
        sb.AppendLine(v.ToString());
        sb.AppendLine();
        sb.AppendLine("Decimal (30 significant digits): " + v.ToScientific(30));
        sb.AppendLine();
        sb.AppendLine($"Numerator digits:   {BigIntLen(v.Num)}");
        sb.AppendLine(v.Den.ToString().Length < 60
            ? $"Denominator:        {v.Den}"
            : $"Denominator digits: {v.Den.ToString().Length}");
        if (n >= 3 && n % 2 == 1)
        {
            sb.AppendLine();
            sb.AppendLine("Odd index >= 3: the value is 0 (Theorem 6.2).");
        }
        var vsc = Rbef.VonStaudtClausen(n, v);
        if (vsc.HasValue)
        {
            sb.AppendLine();
            sb.AppendLine($"von Staudt-Clausen check: {(vsc.Value ? "PASS" : "FAIL")}");
        }
        return sb.ToString();
    }

    private static int BigIntLen(System.Numerics.BigInteger x) =>
        System.Numerics.BigInteger.Abs(x).ToString().Length;

    // ------------------------------------------------------------ Generator
    private void TxtM_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter) BtnGenerator_Click(sender, e);
    }

    private void BtnGenerator_Click(object sender, RoutedEventArgs e)
    {
        if (!int.TryParse(TxtM.Text.Trim(), out int m) || m < 1 || m > Rbef.MaxM)
        {
            MessageBox.Show($"m يجب أن يكون عددًا صحيحًا بين 1 و {Rbef.MaxM}.", "إدخال غير صالح");
            return;
        }
        if (m < 3)
        {
            Out2.Text = "For m < 3 the coefficient row is empty." + Environment.NewLine +
                        "(In the closed form only A(m,m-1) = 1 remains.)";
            return;
        }
        var row = Rbef.GeneratorRow(m);
        var sb = new StringBuilder();
        sb.AppendLine($"Generator row of order m = {m}");
        sb.AppendLine($"k = 1 .. {m - 2}  ({row.Length} entries); the extra entry A({m},{m - 1}) = 1 multiplies C_{m} itself.");
        sb.AppendLine();
        for (int k = 1; k <= row.Length; k++)
            sb.AppendLine($"A({m},{k}) = {row[k - 1]}");
        bool sym = true;
        for (int i = 0; i < row.Length; i++)
            if (row[i] != row[row.Length - 1 - i]) { sym = false; break; }
        sb.AppendLine();
        sb.AppendLine($"Symmetry A(m,k) = A(m,m-1-k): {(sym ? "OK" : "FAILED")}");
        Out2.Text = sb.ToString();
        Status2.Text = $"Done: m = {m}.";
    }

    // ------------------------------------------------------------ helpers
    private void CopyOut1_Click(object s, RoutedEventArgs e) => CopyText(Out1.Text);
    private void CopyOut2_Click(object s, RoutedEventArgs e) => CopyText(Out2.Text);
    private void SaveOut1_Click(object s, RoutedEventArgs e) => SaveText(Out1.Text);
    private void SaveOut2_Click(object s, RoutedEventArgs e) => SaveText(Out2.Text);

    private static void CopyText(string text)
    {
        if (!string.IsNullOrWhiteSpace(text)) Clipboard.SetText(text);
    }

    private static void SaveText(string text)
    {
        var dlg = new SaveFileDialog { Filter = "Text (*.txt)|*.txt", DefaultExt = ".txt" };
        if (dlg.ShowDialog() == true) File.WriteAllText(dlg.FileName, text, Encoding.UTF8);
    }
}
