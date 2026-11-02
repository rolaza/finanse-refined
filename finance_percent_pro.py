import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime, date, timedelta


class MoneyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Finanse | Analiza oszczędności")
        self.geometry("1080x860")
        self.minsize(900, 760)
        self.state("zoomed")
        self.state("zoomed")

        # Spójny, jasny motyw oparty o wbudowany motyw ttk „clam”.
        self.palette = {
            "page": "#f3f6fb", "surface": "#ffffff", "ink": "#17243a",
            "muted": "#68778d", "accent": "#2458c6", "accent_dark": "#1948ad",
            "border": "#dce4ef", "soft": "#edf3ff", "green": "#14805e"
        }
        self.configure(background=self.palette["page"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Page.TFrame", background=self.palette["page"])
        style.configure("Card.TFrame", background=self.palette["surface"])
        style.configure("Hero.TFrame", background="#172b4d")
        style.configure("Title.TLabel", background="#172b4d", foreground="#ffffff",
                        font=("Segoe UI", 21, "bold"))
        style.configure("Subtitle.TLabel", background="#172b4d", foreground="#c4d2e8",
                        font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=self.palette["surface"],
                        foreground=self.palette["ink"], font=("Segoe UI", 12, "bold"))
        style.configure("Body.TLabel", background=self.palette["surface"],
                        foreground=self.palette["muted"], font=("Segoe UI", 9))
        style.configure("Balance.TLabel", background=self.palette["surface"],
                        foreground=self.palette["green"], font=("Segoe UI", 19, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"),
                        foreground="#ffffff", background=self.palette["accent"],
                        borderwidth=0, padding=(16, 10))
        style.map("Primary.TButton", background=[("active", self.palette["accent_dark"])])
        style.configure("Secondary.TButton", font=("Segoe UI", 9, "bold"),
                        foreground=self.palette["accent"], background=self.palette["soft"],
                        borderwidth=0, padding=(12, 8))
        style.map("Secondary.TButton", background=[("active", "#dce8ff")])
        style.configure("Quiet.TButton", font=("Segoe UI", 9),
                        foreground=self.palette["muted"], background=self.palette["surface"],
                        borderwidth=1, padding=(12, 8))
        style.configure("TEntry", padding=8, fieldbackground="#ffffff")

        shell = ttk.Frame(self, style="Page.TFrame", padding=(28, 24))
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(2, weight=1)

        hero = ttk.Frame(shell, style="Hero.TFrame", padding=(24, 20))
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        ttk.Label(hero, text="Finanse", style="Title.TLabel").pack(anchor="w")
        ttk.Label(hero, text="Przejrzysta analiza wpłat i efektywności oszczędzania",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        # Saldo i jego data określają końcowy przepływ pieniężny.
        balance = ttk.Frame(shell, style="Card.TFrame", padding=(20, 15))
        balance.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        balance.columnconfigure(4, weight=1)
        ttk.Label(balance, text="Saldo w dniu", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self.owned_date = tk.StringVar(value=str(date.today()))
        ttk.Entry(balance, textvariable=self.owned_date, width=12).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Button(balance, text="📅", width=3, command=self.choose_owned_date).grid(row=0, column=2, padx=4)
        self.owned_money = tk.StringVar()
        owned_entry = ttk.Entry(balance, textvariable=self.owned_money, width=18)
        owned_entry.grid(row=0, column=3, sticky="w", padx=6)
        owned_entry.bind("<FocusOut>", self.set_owned_money)
        owned_entry.bind("<Return>", self.set_owned_money)
        self.owned_display = ttk.Label(balance, text="0.00", style="Balance.TLabel")
        self.owned_display.grid(row=0, column=5, sticky="e", padx=(18, 2))

        panels = ttk.Frame(shell, style="Page.TFrame")
        panels.grid(row=2, column=0, sticky="nsew")
        panels.columnconfigure(0, weight=1, uniform="panel")
        panels.columnconfigure(1, weight=1, uniform="panel")
        panels.rowconfigure(0, weight=1)

        self.cyclic_amount = tk.StringVar()
        self.cyclic_date = tk.StringVar(value=str(date.today()))
        self.cyclic_end_date = tk.StringVar()
        cyclic_frame = ttk.Frame(panels, style="Card.TFrame", padding=18)
        cyclic_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        cyclic_frame.columnconfigure(0, weight=1)
        cyclic_frame.rowconfigure(2, weight=1)
        ttk.Label(cyclic_frame, text="Wpłaty cykliczne", style="Section.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(cyclic_frame, text="Stała kwota dopisywana co miesiąc",
                  style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 10))
        self.cyclic_list = tk.Listbox(
            cyclic_frame, height=8, font=("Consolas", 9), relief="flat",
            borderwidth=0, highlightthickness=1, highlightbackground=self.palette["border"],
            selectbackground=self.palette["accent"], selectforeground="#ffffff",
            background="#f8faff", foreground=self.palette["ink"], activestyle="none"
        )
        self.cyclic_list.grid(row=2, column=0, sticky="nsew")
        ttk.Button(cyclic_frame, text="Usuń zaznaczoną", style="Quiet.TButton",
                   command=self.delete_cyclic_income).grid(row=3, column=0, sticky="e", pady=8)
        cyclic_add = ttk.Frame(cyclic_frame, style="Card.TFrame")
        cyclic_add.grid(row=4, column=0, sticky="ew", pady=(3, 0))
        cyclic_add.columnconfigure(1, weight=1)
        for row, label, variable in (
            (0, "Kwota", self.cyclic_amount), (1, "Data rozpoczęcia (RRRR-MM-DD)", self.cyclic_date),
            (2, "Data zakończenia (opcjonalnie)", self.cyclic_end_date)
        ):
            ttk.Label(cyclic_add, text=label, style="Body.TLabel").grid(
                row=row, column=0, sticky="w", pady=4, padx=(0, 10))
            ttk.Entry(cyclic_add, textvariable=variable).grid(
                row=row, column=1, sticky="ew", pady=4)
            if row in (1, 2):
                ttk.Button(cyclic_add, text="📅", width=3,
                           command=lambda v=variable: self.choose_date("Wybierz datę", v)).grid(
                    row=row, column=2, padx=(4, 0))
        ttk.Button(cyclic_add, text="Dodaj wpłatę cykliczną", style="Primary.TButton",
                   command=self.add_cyclic_income).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.extra_amount = tk.StringVar()
        self.extra_date = tk.StringVar(value=str(date.today()))
        extra_frame = ttk.Frame(panels, style="Card.TFrame", padding=18)
        extra_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        extra_frame.columnconfigure(0, weight=1)
        extra_frame.rowconfigure(2, weight=1)
        ttk.Label(extra_frame, text="Wpłaty jednorazowe", style="Section.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(extra_frame, text="Dodatkowe wpłaty z wybraną datą",
                  style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 10))
        self.extra_list = tk.Listbox(
            extra_frame, height=8, font=("Consolas", 9), relief="flat",
            borderwidth=0, highlightthickness=1, highlightbackground=self.palette["border"],
            selectbackground=self.palette["accent"], selectforeground="#ffffff",
            background="#f8faff", foreground=self.palette["ink"], activestyle="none"
        )
        self.extra_list.grid(row=2, column=0, sticky="nsew")
        ttk.Button(extra_frame, text="Usuń zaznaczoną", style="Quiet.TButton",
                   command=self.delete_extra_income).grid(row=3, column=0, sticky="e", pady=8)
        extra_add = ttk.Frame(extra_frame, style="Card.TFrame")
        extra_add.grid(row=4, column=0, sticky="ew", pady=(3, 0))
        extra_add.columnconfigure(1, weight=1)
        for row, label, variable in (
            (0, "Kwota", self.extra_amount), (1, "Data wpłaty (RRRR-MM-DD)", self.extra_date)
        ):
            ttk.Label(extra_add, text=label, style="Body.TLabel").grid(
                row=row, column=0, sticky="w", pady=4, padx=(0, 10))
            ttk.Entry(extra_add, textvariable=variable).grid(
                row=row, column=1, sticky="ew", pady=4)
            ttk.Button(extra_add, text="📅", width=3,
                       command=lambda v=variable: self.choose_date("Wybierz datę", v)).grid(
                row=row, column=2, padx=(4, 0))
        ttk.Button(extra_add, text="Dodaj wpłatę jednorazową", style="Primary.TButton",
                   command=self.add_extra_income).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        actions = ttk.Frame(shell, style="Page.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        ttk.Button(actions, text="Oblicz efektywność", style="Primary.TButton",
                   command=self.start_calculation).pack(side="left")
        ttk.Button(actions, text="Prognozuj saldo", style="Primary.TButton",
                   command=self.forecast_balance).pack(side="left", padx=(8, 0))
        utility_buttons = ttk.Frame(actions, style="Page.TFrame")
        utility_buttons.pack(side="right")
        for text, command in (
            ("Zamknij", self.destroy),
            ("Wyczyść wpłaty", self.clear_deposits),
            ("Zapisz wpłaty", self.save_deposits),
            ("Wczytaj wpłaty", self.load_deposits),
        ):
            ttk.Button(utility_buttons, text=text, style="Quiet.TButton",
                       command=command).pack(side="left", padx=(8, 0))

    # ---------- Owned money ----------
    def choose_owned_date(self):
        self.choose_date("Wybierz datę salda", self.owned_date)

    def choose_date(self, title, variable=None, min_date=None):
        try:
            selected = (self.validate_date(variable.get()) if variable is not None else min_date) or date.today()
        except Exception:
            selected = date.today()
        win = tk.Toplevel(self)
        win.title(title)
        year, month = selected.year, selected.month
        header = ttk.Frame(win, padding=8)
        header.pack(fill="x")
        prev_button = ttk.Button(header, text="‹", width=3)
        prev_button.pack(side="left")
        label = ttk.Label(header, text=f"{year}-{month:02d}")
        label.pack(side="left", expand=True)
        next_button = ttk.Button(header, text="›", width=3)
        next_button.pack(side="right")
        manual_date = None
        if min_date is not None:
            manual_frame = ttk.Frame(win, padding=(8, 0))
            manual_frame.pack(fill="x")
            ttk.Label(manual_frame, text="Data (RRRR-MM-DD):").pack(side="left")
            manual_date = tk.StringVar()
            ttk.Entry(manual_frame, textvariable=manual_date, width=12).pack(side="left", padx=6)
            def apply_manual_date():
                chosen = self.validate_date(manual_date.get().strip())
                if chosen is None or chosen <= min_date:
                    messagebox.showerror("Nieprawidłowa data", "Wpisz poprawną datę późniejszą niż data salda.", parent=win)
                    return
                result["date"] = chosen
                win.destroy()
            ttk.Button(manual_frame, text="Użyj daty", command=apply_manual_date).pack(side="left")
        grid = ttk.Frame(win, padding=8)
        grid.pack()
        result = {"date": None}
        def render(y, m):
            for child in grid.winfo_children(): child.destroy()
            label.config(text=f"{y}-{m:02d}")
            prev_button.config(command=lambda: render(y-1 if m == 1 else y, 12 if m == 1 else m-1))
            next_button.config(command=lambda: render(y+1 if m == 12 else y, 1 if m == 12 else m+1))
            for i, name in enumerate(("Pn", "Wt", "Śr", "Cz", "Pt", "So", "Nd")):
                ttk.Label(grid, text=name, width=4, anchor="center").grid(row=0, column=i)
            import calendar
            for week_i, week in enumerate(calendar.monthcalendar(y, m), 1):
                for col, day in enumerate(week):
                    if day:
                        def select_day(d=day, yy=y, mm=m):
                            result["date"] = date(yy, mm, d)
                            if variable is not None:
                                variable.set(result["date"].isoformat())
                            win.destroy()
                        ttk.Button(grid, text=str(day), width=4, command=select_day).grid(row=week_i, column=col)
        render(year, month)
        self.wait_window(win)
        return result["date"]

    def set_owned_money(self, event=None):
        value = self.owned_money.get()
        if not value.strip():
            return
        try:
            amount = float(value)
        except ValueError:
            messagebox.showerror(
                "Nieprawidłowa wartość", "Saldo końcowe musi być liczbą."
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
        today = self.validate_date(self.owned_date.get())
        if today is None:
            messagebox.showerror("Nieprawidłowa data", "Data salda musi mieć format RRRR-MM-DD.")
            return
        return (today.year - d.year) * 12 + (today.month - d.month)

    def next_month(self, current):
        next_year = current.year + (current.month == 12)
        next_month = 1 if current.month == 12 else current.month + 1
        import calendar
        return date(next_year, next_month, min(current.day, calendar.monthrange(next_year, next_month)[1]))

    def format_entry(self, amount, d, end_date=None):
        amount_f = f"{float(amount):8.2f}"
        date_s = d.strftime("%Y-%m-%d")
        months = self.months_ago(d)

        # Zarezerwowane pole daty końcowej utrzymuje wyrównanie kolejnych kolumn.
        end_date_s = end_date.strftime("%Y-%m-%d") if end_date is not None else ""
        if end_date is None and end_date_s == "":
            end_date_s = "—" * 10 if end_date is not None else " " * 10
        return f"{amount_f}  {date_s}  {end_date_s:10}  {months:3d} mies. temu"

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
            raise ValueError("Stopa XIRR nie istnieje lub jest niejednoznaczna.")

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
                "Nie wybrano wpłaty",
                "Zaznacz wpłatę cykliczną, którą chcesz usunąć."
            )
            return

        self.cyclic_list.delete(selection[0])

    def delete_extra_income(self):
        selection = self.extra_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Nie wybrano wpłaty",
                "Zaznacz wpłatę jednorazową, którą chcesz usunąć."
            )
            return

        self.extra_list.delete(selection[0])

    def clear_deposits(self):
        if not messagebox.askyesno("Wyczyść wpłaty", "Czy na pewno usunąć wszystkie wpłaty?"):
            return
        self.cyclic_list.delete(0, tk.END)
        self.extra_list.delete(0, tk.END)

    # ---------- Save / Load deposits ----------
    def save_deposits(self):
        filepath = filedialog.asksaveasfilename(
            title="Zapisz wpłaty",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        data = {
            "cyclic": [],
            "extra": [],
            "balance": float(self.owned_display.cget("text")),
            "balance_date": self.owned_date.get()
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

            messagebox.showinfo("Zapisano", "Wpłaty zostały zapisane.")

        except (OSError, ValueError) as exc:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać wpłat.\\n\\n{exc}")

    def load_deposits(self):
        filepath = filedialog.askopenfilename(
            title="Wczytaj wpłaty",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("Nieprawidłowy format pliku.")

            cyclic = data.get("cyclic", [])
            extra = data.get("extra", [])
            balance = data.get("balance")
            balance_date = data.get("balance_date")

            if not isinstance(cyclic, list) or not isinstance(extra, list):
                raise ValueError("Nieprawidłowe dane wpłat.")
            if balance is not None:
                balance = float(balance)
            if balance_date is not None and self.validate_date(str(balance_date)) is None:
                raise ValueError("Nieprawidłowa data salda.")

            # Validate before replacing the current lists.
            validated_cyclic = []
            for item in cyclic:
                amount = float(item["amount"])
                deposit_date = self.validate_date(str(item["date"]))
                if deposit_date is None:
                    raise ValueError(f"Nieprawidłowa data wpłaty cyklicznej: {item['date']}")

                raw_end_date = item.get("end_date", "")
                end_date = None
                if raw_end_date:
                    end_date = self.validate_date(str(raw_end_date))
                    if end_date is None:
                        raise ValueError(f"Nieprawidłowa data zakończenia wpłaty cyklicznej: {raw_end_date}")
                    if end_date < deposit_date:
                        raise ValueError("Data zakończenia wpłaty cyklicznej nie może być wcześniejsza niż data rozpoczęcia.")

                validated_cyclic.append((amount, deposit_date, end_date))

            validated_extra = []
            for item in extra:
                amount = float(item["amount"])
                deposit_date = self.validate_date(str(item["date"]))
                if deposit_date is None:
                    raise ValueError(f"Nieprawidłowa data wpłaty jednorazowej: {item['date']}")
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

            if balance is not None:
                self.owned_display.config(text=f"{balance:.2f}")
                self.owned_money.set(f"{balance:.2f}")
            if balance_date is not None:
                self.owned_date.set(str(balance_date))

            messagebox.showinfo("Wczytano", "Wpłaty zostały wczytane.")

        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            messagebox.showerror("Błąd wczytywania", f"Nie udało się wczytać wpłat.\\n\\n{exc}")

    # ---------- Actions ----------
    def add_cyclic_income(self):
        if not self.validate_amount(self.cyclic_amount.get()):
            messagebox.showerror("Nieprawidłowa kwota", "Podaj kwotę w formie liczby.")
            return

        d = self.validate_date(self.cyclic_date.get())
        if not d:
            messagebox.showerror("Nieprawidłowa data", "Data rozpoczęcia musi mieć format RRRR-MM-DD.")
            return
        if d > date.today():
            messagebox.showerror("Nieprawidłowa data", "Wpłaty można dodawać tylko z datą z przeszłości lub dzisiejszą.")
            return

        end_date_text = self.cyclic_end_date.get().strip()
        end_date = None

        if end_date_text:
            end_date = self.validate_date(end_date_text)
            if not end_date:
                messagebox.showerror("Nieprawidłowa data", "Data zakończenia musi mieć format RRRR-MM-DD.")
                return

            if end_date < d:
                messagebox.showerror("Nieprawidłowa data", "Data zakończenia nie może być wcześniejsza niż data rozpoczęcia.")
                return

        self.cyclic_list.insert(
            tk.END, self.format_entry(self.cyclic_amount.get(), d, end_date)
        )
        self.cyclic_amount.set("")
        self.cyclic_end_date.set("")

    def add_extra_income(self):
        if not self.validate_amount(self.extra_amount.get()):
            messagebox.showerror("Nieprawidłowa kwota", "Podaj kwotę w formie liczby.")
            return

        d = self.validate_date(self.extra_date.get())
        if not d:
            messagebox.showerror("Nieprawidłowa data", "Data wpłaty musi mieć format RRRR-MM-DD.")
            return
        if d > date.today():
            messagebox.showerror("Nieprawidłowa data", "Wpłaty można dodawać tylko z datą z przeszłości lub dzisiejszą.")
            return

        self.extra_list.insert(
            tk.END, self.format_entry(self.extra_amount.get(), d)
        )
        self.extra_amount.set("")

    def start_calculation(self):
        try:
            owned = float(self.owned_display.cget("text"))
        except ValueError:
            messagebox.showerror("Błąd", "Nie podano salda końcowego.")
            return

        today = self.validate_date(self.owned_date.get())
        if today is None:
            messagebox.showerror("Nieprawidłowa data", "Data salda musi mieć format RRRR-MM-DD.")
            return
        cashflows = []

        # ---- Extra income (past deposits) ----
        for i in range(self.extra_list.size()):
            line = self.extra_list.get(i)
            amount = float(line[:8])
            d = datetime.strptime(line[10:20], "%Y-%m-%d").date()
            if d > today:
                messagebox.showerror("Nieprawidłowa data", "Przy obliczaniu efektywności wszystkie wpłaty muszą przypadać najpóźniej w dniu salda.")
                return
            cashflows.append((d, -amount))

        # ---- Cyclic income (monthly deposits) ----
        for i in range(self.cyclic_list.size()):
            line = self.cyclic_list.get(i)
            parts = line.split()
            amount = float(parts[0])
            start = datetime.strptime(parts[1], "%Y-%m-%d").date()
            if start > today:
                messagebox.showerror("Nieprawidłowa data", "Przy obliczaniu efektywności wszystkie wpłaty muszą przypadać najpóźniej w dniu salda.")
                return

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
            messagebox.showerror("Błąd", "Za mało danych do obliczeń.")
            return

        #            rate = self.calculate_xirr(cashflows)
        try:
            rate = self.xirr_bisection(cashflows)
        except ValueError:
            messagebox.showerror(
                "Błąd obliczeń",
                "Nie można jednoznacznie wyznaczyć stopy zwrotu dla podanych przepływów pieniężnych."
            )
            return

        messagebox.showinfo(
            "Efektywność oszczędzania",
            f"Średnia roczna stopa zwrotu:\n\n{rate * 100:.2f}%"
        )

    def forecast_balance(self):
        balance_date = self.validate_date(self.owned_date.get())
        if balance_date is None:
            messagebox.showerror("Nieprawidłowa data", "Data salda musi mieć format RRRR-MM-DD.")
            return
        try:
            balance = float(self.owned_display.cget("text"))
        except ValueError:
            messagebox.showerror("Błąd", "Nie podano salda.")
            return
        target = self.choose_date("Wybierz datę prognozy", min_date=balance_date)
        if target is None:
            return
        if target <= balance_date:
            messagebox.showerror("Nieprawidłowa data", "Data prognozy musi być późniejsza niż data salda.")
            return
        # Estimate annual return from historical deposits and the stated balance date.
        cashflows = []
        for i in range(self.extra_list.size()):
            line = self.extra_list.get(i)
            deposit_date = datetime.strptime(line[10:20], "%Y-%m-%d").date()
            if deposit_date > balance_date:
                messagebox.showerror("Nieprawidłowa data", "Przy prognozie wpłaty muszą przypadać najpóźniej w dniu salda.")
                return
            cashflows.append((deposit_date, -float(line[:8])))
        for i in range(self.cyclic_list.size()):
            parts = self.cyclic_list.get(i).split()
            amount, start = float(parts[0]), date.fromisoformat(parts[1])
            if start > balance_date:
                messagebox.showerror("Nieprawidłowa data", "Przy prognozie wpłaty muszą przypadać najpóźniej w dniu salda.")
                return
            end = date.fromisoformat(parts[2]) if len(parts) >= 3 and self.validate_date(parts[2]) else balance_date
            current = start
            while current <= min(end, balance_date):
                cashflows.append((current, -amount))
                current = self.next_month(current)
        cashflows.append((balance_date, balance))
        cashflows.sort(key=lambda item: item[0])
        try:
            rate = self.xirr_bisection(cashflows)
        except ValueError:
            messagebox.showerror("Błąd obliczeń", "Nie można wyznaczyć stopy zwrotu z podanych wpłat.")
            return
        value = balance * (1 + rate) ** ((target - balance_date).days / 365.25)
        for i in range(self.cyclic_list.size()):
            parts = self.cyclic_list.get(i).split()
            amount, start = float(parts[0]), date.fromisoformat(parts[1])
            end = date.fromisoformat(parts[2]) if len(parts) >= 3 and self.validate_date(parts[2]) else target
            current = self.next_month(start)
            while current <= balance_date:
                current = self.next_month(current)
            while current <= min(end, target):
                value += amount * (1 + rate) ** ((target - current).days / 365.25)
                current = self.next_month(current)
        messagebox.showinfo("Prognoza salda", f"Przewidywane saldo na {target:%Y-%m-%d}:\n\n{value:.2f}")


if __name__ == "__main__":
    MoneyApp().mainloop()
