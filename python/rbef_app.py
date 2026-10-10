"""
RBEF Calculator - Windows desktop application (Tkinter).

Tab 1  Bernoulli number: enter the index n, get B_n computed by the RBEF
       recurrence (Corollary 4.3 of the paper), as an exact fraction.
Tab 2  Generator row:    enter the exponent m, get the coefficients
       A(m,k) = binom(m,k)/(k+1), k = 1..m-2, built from one half by symmetry.

The mathematics lives in rbef_reference.py (verified up to m = 300).
Requires Python >= 3.8 with Tkinter (included in the standard Windows installer).
"""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from rbef_logic import (MAX_M, MAX_N, bernoulli, generator_values, to_decimal,
                        von_staudt_ok)

# ----------------------------------------------------------------- GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RBEF Calculator")
        self.geometry("900x640")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        self.tab1 = ttk.Frame(nb)
        self.tab2 = ttk.Frame(nb)
        nb.add(self.tab1, text="Bernoulli number")
        nb.add(self.tab2, text="Generator row")
        self._build_tab1()
        self._build_tab2()

    # ---- tab 1
    def _build_tab1(self):
        f = self.tab1
        top = ttk.Frame(f)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Index n:").pack(side="left")
        self.n_var = tk.StringVar(value="100")
        e = ttk.Entry(top, textvariable=self.n_var, width=8)
        e.pack(side="left", padx=6)
        e.bind("<Return>", lambda _e: self.run_bernoulli())
        self.plus_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Use B1 = +1/2 (RBEF value C1)",
                        variable=self.plus_var).pack(side="left", padx=10)
        self.b_btn = ttk.Button(top, text="Compute", command=self.run_bernoulli)
        self.b_btn.pack(side="left")
        ttk.Button(top, text="Copy", command=lambda: self.copy(self.out1)
                   ).pack(side="left", padx=6)
        ttk.Button(top, text="Save...", command=lambda: self.save(self.out1)
                   ).pack(side="left")
        self.status1 = ttk.Label(f, text="Enter n (0 to %d) and press Compute." % MAX_N)
        self.status1.pack(anchor="w", padx=10)
        self.out1 = self._text(f)

    def run_bernoulli(self):
        try:
            n = int(self.n_var.get())
            if not 0 <= n <= MAX_N:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input", "n must be an integer between 0 and %d." % MAX_N)
            return
        self.b_btn.config(state="disabled")
        self.status1.config(text="Computing B_%d ..." % n)
        plus = self.plus_var.get()

        def work():
            try:
                v = bernoulli(n, plus_one_half=plus)
                self.after(0, lambda: self.show_bernoulli(n, v, plus))
            except Exception as ex:                      # pragma: no cover
                self.after(0, lambda: messagebox.showerror("Error", str(ex)))
                self.after(0, lambda: self.b_btn.config(state="normal"))
        threading.Thread(target=work, daemon=True).start()

    def show_bernoulli(self, n, v, plus):
        vs = von_staudt_ok(n, v)
        lines = ["B_%d  (RBEF recurrence, a0 = d = 1)" % n, ""]
        if n == 1:
            lines.append("convention: B1 = %s" % ("+1/2" if plus else "-1/2"))
            lines.append("")
        lines.append("Exact value:")
        lines.append(str(v) if v.denominator != 1 else str(v.numerator))
        lines.append("")
        lines.append("Decimal (30 significant digits): " + to_decimal(v))
        lines.append("")
        lines.append("Numerator digits:   %d" % len(str(abs(v.numerator))))
        lines.append("Denominator:        %s" % v.denominator
                     if len(str(v.denominator)) < 60 else "Denominator digits: %d" % len(str(v.denominator)))
        if n >= 3 and n % 2:
            lines.append("")
            lines.append("Odd index >= 3: the value is 0 (Theorem 6.2).")
        if vs is not None:
            lines.append("")
            lines.append("von Staudt-Clausen check: %s" % ("PASS" if vs else "FAIL"))
        self.set_text(self.out1, "\n".join(lines))
        self.status1.config(text="Done.")
        self.b_btn.config(state="normal")

    # ---- tab 2
    def _build_tab2(self):
        f = self.tab2
        top = ttk.Frame(f)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Exponent m:").pack(side="left")
        self.m_var = tk.StringVar(value="8")
        e = ttk.Entry(top, textvariable=self.m_var, width=8)
        e.pack(side="left", padx=6)
        e.bind("<Return>", lambda _e: self.run_generator())
        ttk.Button(top, text="Compute", command=self.run_generator).pack(side="left")
        ttk.Button(top, text="Copy", command=lambda: self.copy(self.out2)
                   ).pack(side="left", padx=6)
        ttk.Button(top, text="Save...", command=lambda: self.save(self.out2)
                   ).pack(side="left")
        self.status2 = ttk.Label(
            f, text="A(m,k) = C(m,k)/(k+1) = C(m+1,k+1)/(m+1), k = 1..m-2 (m >= 3).")
        self.status2.pack(anchor="w", padx=10)
        self.out2 = self._text(f)

    def run_generator(self):
        try:
            m = int(self.m_var.get())
            if not 1 <= m <= MAX_M:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input", "m must be an integer between 1 and %d." % MAX_M)
            return
        if m < 3:
            self.set_text(self.out2, "For m < 3 the coefficient row is empty.\n"
                                     "(In the closed form, only A(m,m-1) = 1 remains.)")
            return
        vals = generator_values(m)
        lines = ["Generator row of order m = %d" % m,
                 "k = 1 .. %d  (%d entries); the extra entry A(%d,%d) = 1 multiplies C_%d itself."
                 % (m - 2, len(vals), m, m - 1, m), ""]
        for k, a in vals:
            lines.append("A(%d,%d) = %s" % (m, k, a if a.denominator != 1 else a.numerator))
        sym = all(vals[i][1] == vals[-1 - i][1] for i in range(len(vals)))
        lines += ["", "Symmetry A(m,k) = A(m,m-1-k): %s" % ("OK" if sym else "FAILED")]
        self.set_text(self.out2, "\n".join(lines))
        self.status2.config(text="Done: m = %d." % m)

    # ---- helpers
    def _text(self, parent):
        fr = ttk.Frame(parent)
        fr.pack(fill="both", expand=True, padx=8, pady=8)
        t = tk.Text(fr, wrap="word", font=("Consolas", 11))
        sb = ttk.Scrollbar(fr, command=t.yview)
        t.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        t.pack(side="left", fill="both", expand=True)
        return t

    @staticmethod
    def set_text(widget, s):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", s)

    def copy(self, widget):
        self.clipboard_clear()
        self.clipboard_append(widget.get("1.0", "end").strip())

    def save(self, widget):
        p = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Text", "*.txt")])
        if p:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(widget.get("1.0", "end"))


if __name__ == "__main__":
    App().mainloop()
