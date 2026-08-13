import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime, date, timedelta


class MoneyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Money App")
        self.geometry("690x720")

        mono_font = ("Courier New", 10)

        # ---- Owned money ----
        owned_frame = ttk.LabelFrame(self, text="Final balance")
        owned_frame.pack(fill="x", padx=10, pady=5)

        owned_inner = ttk.Frame(owned_frame)
        owned_inner.pack(fill="x", padx=10, pady=5)

        self.owned_money = tk.StringVar()

        ttk.Entry(
            owned_inner,
            textvariable=self.owned_money,
            width=20
        ).pack(side="left")

        ttk.Button(
            owned_inner,
            text="Set",
            command=self.set_owned_money
        ).pack(side="left", padx=5)

        self.owned_display = ttk.Label(
            owned_inner, text="0.00", font=("Courier New", 11, "bold")
        )
        self.owned_display.pack(side="left", padx=10)

        # ---- Cyclic income ----
        cyclic_frame = ttk.LabelFrame(self, text="Cyclic deposit (once a month)")
        cyclic_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.cyclic_list = tk.Listbox(
            cyclic_frame, height=6, font=mono_font
        )
        self.cyclic_list.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(
            cyclic_frame,
            text="DELETE SELECTED",
            command=self.delete_cyclic_income
        ).pack(pady=(0, 5))

        cyclic_add = ttk.Frame(cyclic_frame)
        cyclic_add.pack(fill="x", padx=5, pady=5)

        self.cyclic_amount = tk.StringVar()
        self.cyclic_date = tk.StringVar(value=str(date.today()))

        ttk.Label(cyclic_add, text="Amount").grid(row=0, column=0, sticky="w")
        ttk.Entry(cyclic_add, textvariable=self.cyclic_amount).grid(
            row=0, column=1, sticky="ew", padx=5
        )

        ttk.Label(cyclic_add, text="Start date (YYYY-MM-DD)").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Entry(cyclic_add, textvariable=self.cyclic_date).grid(
            row=1, column=1, sticky="ew", padx=5
        )

        ttk.Label(cyclic_add, text="End date (YYYY-MM-DD, optional)").grid(
            row=2, column=0, sticky="w"
        )
        self.cyclic_end_date = tk.StringVar()
        ttk.Entry(cyclic_add, textvariable=self.cyclic_end_date).grid(
            row=2, column=1, sticky="ew", padx=5
        )

        ttk.Button(
            cyclic_add, text="Add", command=self.add_cyclic_income
        ).grid(row=3, column=0, columnspan=2, pady=5)

        cyclic_add.columnconfigure(1, weight=1)

        # ---- Extra income ----
        extra_frame = ttk.LabelFrame(self, text="Extra deposit (one-time)")
        extra_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.extra_list = tk.Listbox(
            extra_frame, height=6, font=mono_font
        )
        self.extra_list.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(
            extra_frame,
            text="DELETE SELECTED",
            command=self.delete_extra_income
        ).pack(pady=(0, 5))

        extra_add = ttk.Frame(extra_frame)
        extra_add.pack(fill="x", padx=5, pady=5)

        self.extra_amount = tk.StringVar()
        self.extra_date = tk.StringVar(value=str(date.today()))

        ttk.Label(extra_add, text="Amount").grid(row=0, column=0, sticky="w")
        ttk.Entry(extra_add, textvariable=self.extra_amount).grid(
            row=0, column=1, sticky="ew", padx=5
        )

        ttk.Label(extra_add, text="Date (YYYY-MM-DD)").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Entry(extra_add, textvariable=self.extra_date).grid(
            row=1, column=1, sticky="ew", padx=5
        )

        ttk.Button(
            extra_add, text="Add", command=self.add_extra_income
        ).grid(row=2, column=0, columnspan=2, pady=5)

        extra_add.columnconfigure(1, weight=1)

        # ---- Large buttons (balanced size) ----
        buttons = ttk.Frame(self)
        buttons.pack(pady=15)

        style = ttk.Style()
        style.configure(
            "Big.TButton",
            font=("Segoe UI", 10, "bold")
        )

        ttk.Button(
            buttons,
            text="START",
            width=20,
            style="Big.TButton",
            command=self.start_calculation
        ).pack(side="left", padx=12, ipady=3)

        ttk.Button(
            buttons,
            text="EXIT",
            width=20,
            command=self.destroy,
            style="Big.TButton"
        ).pack(side="left", padx=12, ipady=3)

        ttk.Button(
            buttons,
            text="SAVE DEPOSITS",
            width=20,
            command=self.save_deposits,
            style="Big.TButton"
        ).pack(side="left", padx=12, ipady=3)

        ttk.Button(
            buttons,
            text="LOAD DEPOSITS",
            width=20,
            command=self.load_deposits,
            style="Big.TButton"
        ).pack(side="left", padx=12, ipady=3)

    # ---------- Owned money ----------
    def set_owned_money(self):
        value = self.owned_money.get()
        try:
            amount = float(value)
        except ValueError:
            messagebox.showerror(
                "Invalid value", "Owned money must be a number."
            )
            return

        formatted = f"{amount:.2f}"
        self.owned_display.config(text=formatted)
        self.owned_money.set(formatted)

    # ---------- Helpers ----------
    def validate_amount(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def validate_date(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def months_ago(self, d):
        today = date.today()
        return (today.year - d.year) * 12 + (today.month - d.month)

    def format_entry(self, amount, d, end_date=None):
        amount_f = f"{float(amount):8.2f}"
        date_s = d.strftime("%Y-%m-%d")
        months = self.months_ago(d)

        if end_date is not None:
            return f"{amount_f}  {date_s}  {end_date.strftime('%Y-%m-%d')}  {months:3d} months ago"

        return f"{amount_f}  {date_s}  {months:3d} months ago"

    def calculate_xirr(self, cashflows):
        """
        cashflows: list of (date, amount)
        returns yearly interest rate (float)
        """

        def npv(rate):
            base_date = cashflows[0][0]
            total = 0.0
            for d, amt in cashflows:
                years = (d - base_date).days / 365.25
                total += amt / ((1 + rate) ** years)
            return total

        rate = 0.1  # initial guess: 10%
        for _ in range(100):
            f = npv(rate)
            # numerical derivative
            df = (npv(rate + 1e-6) - f) / 1e-6
            if abs(df) < 1e-10:
                break
            rate -= f / df
        return rate

    def xirr_bisection(self, cashflows, lo=-0.9999, hi=10.0):
        def npv(rate):
            base = cashflows[0][0]
            total = 0.0
            for d, amt in cashflows:
                years = (d - base).days / 365.25
                total += amt / ((1 + rate) ** years)
            return total

        f_lo = npv(lo)
        f_hi = npv(hi)

        if f_lo * f_hi > 0:
            raise ValueError("XIRR does not exist or is ambiguous")

        for _ in range(100):
            mid = (lo + hi) / 2
            f_mid = npv(mid)

            if abs(f_mid) < 1e-7:
                return mid

            if f_lo * f_mid < 0:
                hi = mid
                f_hi = f_mid
            else:
                lo = mid
                f_lo = f_mid

        return (lo + hi) / 2

    # ---------- Delete deposits ----------
    def delete_cyclic_income(self):
        selection = self.cyclic_list.curselection()

        if not selection:
            messagebox.showwarning(
                "No selection",
                "Select a cyclic deposit to delete."
            )
            return

        self.cyclic_list.delete(selection[0])

    def delete_extra_income(self):
        selection = self.extra_list.curselection()

        if not selection:
            messagebox.showwarning(
                "No selection",
                "Select an extra deposit to delete."
            )
            return

        self.extra_list.delete(selection[0])

    # ---------- Save / Load deposits ----------
    def save_deposits(self):
        filepath = filedialog.asksaveasfilename(
            title="Save deposits",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        data = {
            "cyclic": [],
            "extra": []
        }

        # Save only deposits: amount and date.
        for i in range(self.cyclic_list.size()):
            line = self.cyclic_list.get(i)
            parts = line.split()
            amount = float(parts[0])
            deposit_date = parts[1]
            end_date = ""
            if len(parts) >= 3 and self.validate_date(parts[2]):
                end_date = parts[2]
            data["cyclic"].append({
                "amount": amount,
                "date": deposit_date,
                "end_date": end_date
            })

        for i in range(self.extra_list.size()):
            line = self.extra_list.get(i)
            amount = float(line[:8])
            deposit_date = line[10:20]
            data["extra"].append({
                "amount": amount,
                "date": deposit_date
            })

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            messagebox.showinfo("Saved", "Deposits saved successfully.")

        except (OSError, ValueError) as exc:
            messagebox.showerror("Save error", f"Could not save deposits.\\n\\n{exc}")

    def load_deposits(self):
        filepath = filedialog.askopenfilename(
            title="Load deposits",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("Invalid file format.")

            cyclic = data.get("cyclic", [])
            extra = data.get("extra", [])

            if not isinstance(cyclic, list) or not isinstance(extra, list):
                raise ValueError("Invalid deposit data.")

            # Validate before replacing the current lists.
            validated_cyclic = []
            for item in cyclic:
                amount = float(item["amount"])
                deposit_date = self.validate_date(str(item["date"]))
                if deposit_date is None:
                    raise ValueError(f"Invalid cyclic deposit date: {item['date']}")

                raw_end_date = item.get("end_date", "")
                end_date = None
                if raw_end_date:
                    end_date = self.validate_date(str(raw_end_date))
                    if end_date is None:
                        raise ValueError(f"Invalid cyclic deposit end date: {raw_end_date}")
                    if end_date < deposit_date:
                        raise ValueError("Cyclic deposit end date cannot be before start date.")

                validated_cyclic.append((amount, deposit_date, end_date))

            validated_extra = []
            for item in extra:
                amount = float(item["amount"])
                deposit_date = self.validate_date(str(item["date"]))
                if deposit_date is None:
                    raise ValueError(f"Invalid extra deposit date: {item['date']}")
                validated_extra.append((amount, deposit_date))

            # Replace only the deposit lists.
            # Final balance is deliberately not changed.
            self.cyclic_list.delete(0, tk.END)
            self.extra_list.delete(0, tk.END)

            for amount, deposit_date, end_date in validated_cyclic:
                self.cyclic_list.insert(
                    tk.END, self.format_entry(amount, deposit_date, end_date)
                )

            for amount, deposit_date in validated_extra:
                self.extra_list.insert(
                    tk.END, self.format_entry(amount, deposit_date)
                )

            messagebox.showinfo("Loaded", "Deposits loaded successfully.")

        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            messagebox.showerror("Load error", f"Could not load deposits.\\n\\n{exc}")

    # ---------- Actions ----------
    def add_cyclic_income(self):
        if not self.validate_amount(self.cyclic_amount.get()):
            messagebox.showerror("Invalid amount", "Amount is missing or not a number.")
            return

        d = self.validate_date(self.cyclic_date.get())
        if not d:
            messagebox.showerror("Invalid date", "Start date must be YYYY-MM-DD.")
            return

        end_date_text = self.cyclic_end_date.get().strip()
        end_date = None

        if end_date_text:
            end_date = self.validate_date(end_date_text)
            if not end_date:
                messagebox.showerror("Invalid date", "End date must be YYYY-MM-DD.")
                return

            if end_date < d:
                messagebox.showerror("Invalid date", "End date cannot be before start date.")
                return

        self.cyclic_list.insert(
            tk.END, self.format_entry(self.cyclic_amount.get(), d, end_date)
        )
        self.cyclic_amount.set("")
        self.cyclic_end_date.set("")

    def add_extra_income(self):
        if not self.validate_amount(self.extra_amount.get()):
            messagebox.showerror("Invalid amount", "Amount is missing or not a number.")
            return

        d = self.validate_date(self.extra_date.get())
        if not d:
            messagebox.showerror("Invalid date", "Date must be YYYY-MM-DD.")
            return

        self.extra_list.insert(
            tk.END, self.format_entry(self.extra_amount.get(), d)
        )
        self.extra_amount.set("")

    def start_calculation(self):
        try:
            owned = float(self.owned_display.cget("text"))
        except ValueError:
            messagebox.showerror("Error", "Owned money not set.")
            return

        today = date.today()
        cashflows = []

        # ---- Extra income (past deposits) ----
        for i in range(self.extra_list.size()):
            line = self.extra_list.get(i)
            amount = float(line[:8])
            d = datetime.strptime(line[10:20], "%Y-%m-%d").date()
            cashflows.append((d, -amount))

        # ---- Cyclic income (monthly deposits) ----
        for i in range(self.cyclic_list.size()):
            line = self.cyclic_list.get(i)
            parts = line.split()
            amount = float(parts[0])
            start = datetime.strptime(parts[1], "%Y-%m-%d").date()

            # Empty end date means the deposit repeats through today.
            end_date = None
            if len(parts) >= 3 and self.validate_date(parts[2]):
                end_date = datetime.strptime(
                    parts[2], "%Y-%m-%d"
                ).date()

            last_date = today if end_date is None else min(end_date, today)

            current = start
            while current <= last_date:
                cashflows.append((current, -amount))
                # Advance one month, keeping the original day when possible.
                # If that day does not exist in the next month, use its last day.
                if current.month == 12:
                    next_year = current.year + 1
                    next_month = 1
                else:
                    next_year = current.year
                    next_month = current.month + 1
                if next_month == 12:
                    following_year = next_year + 1
                    following_month = 1
                else:
                    following_year = next_year
                    following_month = next_month + 1
                last_day = (
                    date(following_year, following_month, 1)
                    - timedelta(days=1)
                ).day
                next_day = min(current.day, last_day)
                current = date(next_year, next_month, next_day)

        # ---- Final value ----
        cashflows.append((today, owned))

        cashflows.sort(key=lambda x: x[0])

        if len(cashflows) < 2:
            messagebox.showerror("Error", "Not enough data.")
            return

        #            rate = self.calculate_xirr(cashflows)
        try:
            rate = self.xirr_bisection(cashflows)
        except ValueError:
            messagebox.showerror(
                "Calculation error",
                "Rate of return is undefined or ambiguous for given cashflows."
            )
            return

        messagebox.showinfo(
            "Account efficiency",
            f"Average yearly interest:\n\n{rate * 100:.2f}%"
        )


if __name__ == "__main__":
    MoneyApp().mainloop()