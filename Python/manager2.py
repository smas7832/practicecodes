#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Feature-rich Expense Manager GUI
-------------------------------
Budgets, charts, recurring expenses, search, CSV/Excel export, reminders.
Works on Windows 11 and any OS with Python.
"""

import json, os, datetime as dt, csv, re, queue, threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox as mb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plyer import notification  # Windows balloon

DATA_FILE      = "expenses.json"
BUDGET_FILE    = "budgets.json"
RECUR_FILE     = "recurring.json"

# ------------------------------------------------------------------
# Helper: date utils
# ------------------------------------------------------------------
def month_str(d: dt.date) -> str:
    return d.strftime("%Y-%m")

# ------------------------------------------------------------------
# Main app
# ------------------------------------------------------------------
class ExpenseManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.style = tb.Style("flatly")
        self.dark = False
        self.title("Expense Manager")
        self.geometry("950x650")
        self.minsize(800, 500)

        # data containers
        self.categories = []
        self.expenses   = []
        self.budgets    = {}        # { (year-month, category): amount }
        self.recurring    = []      # list of dicts
        self._next_id     = 1
        self._load_everything()

        # search state
        self.search_filters = {}

        self.create_widgets()
        self.start_recurring_daemon()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def create_widgets(self):
        # ---------- toolbar ------------------------------------------------
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=5, pady=5)

        for t, cmd in (
                ("Add", self.add_expense),
                ("Edit", self.edit_expense),
                ("Delete", self.delete_expense),
                ("Add Category", self.add_category),
                ("Set Budget", self.set_budget),
                ("Recurring", self.manage_recurring),
                ("Charts", self.show_charts),
                ("Export", self.export_data),
                ("Search", self.search_dlg),
        ):
            ttk.Button(bar, text=t, command=cmd).pack(side="left", padx=2)

        ttk.Button(bar, text="Switch to Dark", command=self.toggle_theme).pack(
            side="right", padx=5
        )

        # ---------- main notebook -----------------------------------------
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=5, pady=5)

        # --- tab 1 : list
        frm_list = ttk.Frame(nb)
        nb.add(frm_list, text="Expenses")
        self.create_tree(frm_list)

        # --- tab 2 : charts
        frm_charts = ttk.Frame(nb)
        nb.add(frm_charts, text="Charts")
        self.chart_frame = frm_charts

    def create_tree(self, parent):
        columns = ("date", "amount", "category", "note")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings",
                               selectmode="browse")
        self.tree.pack(fill="both", expand=True)
        for c, w in zip(columns, (120, 100, 120, 300)):
            self.tree.column(c, width=w, anchor="w")
            self.tree.heading(c, text=c.capitalize())

        self.tree.bind("<Double-1>", lambda e: self.edit_expense())
        self.tree.bind("<Button-3>", self.popup_menu)

        self.refresh_tree()

    # ------------------------------------------------------------------
    # data loading / saving
    # ------------------------------------------------------------------
    def _load_everything(self):
        # categories
        self.categories = list(set([e["category"] for e in self._load_json(DATA_FILE)])) or \
                          ["Food","Transport","Entertainment","Bills","Health","Shopping","Other"]
        # expenses
        self.expenses = self._load_json(DATA_FILE)
        ids = [e.get("id", 0) for e in self.expenses]
        self._next_id = max(ids, default=0) + 1
        # budgets
        self.budgets = {(tuple(k.split("-"))): v for k, v in
                        self._load_json(BUDGET_FILE).items()}
        # recurring
        self.recurring = self._load_json(RECUR_FILE)

    def _save_expenses(self):
        self._save_json(DATA_FILE, self.expenses)

    def _save_budgets(self):
        serial = {"-".join(k): v for k, v in self.budgets.items()}
        self._save_json(BUDGET_FILE, serial)

    def _save_recurring(self):
        self._save_json(RECUR_FILE, self.recurring)

    @staticmethod
    def _load_json(name):
        try:
            with open(name, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return [] if name != BUDGET_FILE else {}

    @staticmethod
    def _save_json(name, obj):
        with open(name, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # tree helpers
    # ------------------------------------------------------------------
    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        q = self.expenses
        # apply filters
        for f in self.search_filters.values():
            q = list(filter(f, q))
        for e in q:
            self.tree.insert(
                "", "end", iid=str(e["id"]),
                values=(e["date"], f"{e['amount']:.2f}",
                        e["category"], e["note"])
            )
        # check budgets
        self.check_budgets()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def add_expense(self):
        d = ExpenseDialog(self, title="Add Expense", categories=self.categories).result
        if d:
            d["id"] = self._next_id; self._next_id += 1
            self.expenses.append(d)
            self._save_expenses()
            self.refresh_tree()

    def edit_expense(self):
        sel = self.tree.selection()
        if not sel:
            return mb.show_info("Select an expense to edit.")
        exp = next(e for e in self.expenses if e["id"] == int(sel[0]))
        d = ExpenseDialog(self, title="Edit Expense", categories=self.categories,
                          init_data=exp).result
        if d:
            for k in d:
                exp[k] = d[k]
            self._save_expenses()
            self.refresh_tree()

    def delete_expense(self):
        sel = self.tree.selection()
        if not sel:
            return mb.show_info("Select an expense to delete.")
        if mb.yesno("Confirm", "Delete selected expense?"):
            self.expenses = [e for e in self.expenses if e["id"] != int(sel[0])]
            self._save_expenses()
            self.refresh_tree()

    def add_category(self):
        cat = simpledialog.askstring("Add Category", "Category name:", parent=self)
        if cat and cat.strip() and cat not in self.categories:
            self.categories.append(cat)

    # ------------------------------------------------------------------
    # budgets
    # ------------------------------------------------------------------
    def set_budget(self):
        month = simpledialog.askstring("Budget", "Month (YYYY-MM):", parent=self,
                                     initialvalue=month_str(dt.date.today()))
        cat = simpledialog.askstring("Budget", "Category:", parent=self,
                                   initialvalue=self.categories[0])
        amt = simpledialog.askfloat("Budget", "Amount:", parent=self)
        if month and cat and amt is not None:
            self.budgets[(month, cat)] = amt
            self._save_budgets()
            self.check_budgets()

    def check_budgets(self):
        # group expenses by month & category
        grouped = {}
        for e in self.expenses:
            key = (e["date"][:7], e["category"])
            grouped[key] = grouped.get(key, 0) + e["amount"]
        for (month, cat), spent in grouped.items():
            b = self.budgets.get((month, cat))
            if b and spent > b:
                msg = f"You overspent {cat} budget for {month} by " \
                      f"{spent-b:.2f}"
                notification.notify(
                    title="Budget Alert", message=msg, timeout=4
                )

    # ------------------------------------------------------------------
    # recurring expenses
    # ------------------------------------------------------------------
    def manage_recurring(self):
        RecurringDialog(self)

    def start_recurring_daemon(self):
        self.recur_q = queue.Queue()
        threading.Thread(target=self._recur_loop, daemon=True).start()
        self.after(1000, self._process_recur_queue)

    def _recur_loop(self):
        while True:
            today = dt.date.today()
            for r in self.recurring:
                if r.get("last") is None:
                    r["last"] = r["start"]
                last = dt.datetime.fromisoformat(r["last"]).date()
                delta = dt.timedelta(days=r["every"])
                while last + delta <= today:
                    last += delta
                    self.expenses.append({
                        "date": last.isoformat(),
                        "amount": r["amount"],
                        "category": r["category"],
                        "note": f"Recurring: {r['note']}",
                        "id": self._next_id
                    })
                    self._next_id += 1
                    self.recur_q.put("new")
                r["last"] = last.isoformat()
            self._save_expenses()
            self._save_recurring()
            threading.Event().wait(3600)  # sleep 1h

    def _process_recur_queue(self):
        try:
            while True:
                self.recur_q.get_nowait()
                self.refresh_tree()
        except queue.Empty:
            pass
        self.after(5000, self._process_recur_queue)

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------
    def search_dlg(self):
        SearchDialog(self)

    # ------------------------------------------------------------------
    # export
    # ------------------------------------------------------------------
    def export_data(self):
        f = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")])
        if not f:
            return
        df = pd.DataFrame(self.expenses)
        if f.lower().endswith(".csv"):
            df.to_csv(f, index=False)
        else:
            df.to_excel(f, index=False)
        mb.show_info("Export", "File saved.")

    # ------------------------------------------------------------------
    # charts
    # ------------------------------------------------------------------
    def show_charts(self):
        ChartsDialog(self)

    # ------------------------------------------------------------------
    # theme
    # ------------------------------------------------------------------
    def toggle_theme(self):
        self.dark = not self.dark
        self.style.theme_use("darkly" if self.dark else "flatly")

    # ------------------------------------------------------------------
    # popup menu
    # ------------------------------------------------------------------
    def popup_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            m = tk.Menu(self, tearoff=0)
            m.add_command(label="Edit", command=self.edit_expense)
            m.add_command(label="Delete", command=self.delete_expense)
            m.tk_popup(event.x_root, event.y_root)


# ------------------------------------------------------------------
# Dialogs
# ------------------------------------------------------------------
class ExpenseDialog(tk.Toplevel):
    def __init__(self, parent, title, categories, init_data=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.categories = categories

        vars = "date", "amount", "category", "note"
        self.v = {k: tk.StringVar() for k in vars}
        self.v["amount"] = tk.DoubleVar()
        today = dt.date.today().isoformat()
        self.v["date"].set(init_data["date"] if init_data else today)
        self.v["amount"].set(init_data["amount"] if init_data else 0.0)
        self.v["category"].set(init_data["category"] if init_data else categories[0])
        self.v["note"].set(init_data["note"] if init_data else "")

        frm = ttk.Frame(self, padding=10)
        frm.pack()
        ttk.Label(frm, text="Date").grid(row=0, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.v["date"]).grid(row=0, column=1)
        ttk.Label(frm, text="Amount").grid(row=1, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.v["amount"]).grid(row=1, column=1)
        ttk.Label(frm, text="Category").grid(row=2, column=0, sticky="e")
        ttk.Combobox(frm, textvariable=self.v["category"],
                     values=categories, state="readonly").grid(row=2, column=1)
        ttk.Label(frm, text="Note").grid(row=3, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.v["note"]).grid(row=3, column=1)

        ttk.Button(frm, text="OK", command=self.ok).grid(row=4, column=1, sticky="e")
        ttk.Button(frm, text="Cancel", command=self.destroy).grid(row=4, column=0)
        self.bind("<Return>", lambda e: self.ok())
        self.bind("<Escape>", lambda e: self.destroy())

    def ok(self):
        try:
            dt.datetime.strptime(self.v["date"].get(), "%Y-%m-%d")
            amount = float(self.v["amount"].get())
            cat = self.v["category"].get()
            if cat not in self.categories:
                raise ValueError
            self.result = {
                "date": self.v["date"].get(),
                "amount": amount,
                "category": cat,
                "note": self.v["note"].get()
            }
            self.destroy()
        except Exception:
            mb.show_error("Error", "Please enter valid data.")


class RecurringDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Recurring Expenses")
        self.parent = parent
        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)
        listbox = tk.Listbox(frm, height=10)
        listbox.pack(fill="both", expand=True)

        for r in parent.recurring:
            listbox.insert("end", f"{r['note']} | {r['category']} | every {r['every']} days")

        ttk.Button(frm, text="Add new",
                   command=self.add).pack(side="left", pady=5)
        ttk.Button(frm, text="Close", command=self.destroy).pack(side="right", pady=5)

    def add(self):
        d = ExpenseDialog(self, "Add Recurring", categories=self.parent.categories).result
        if d:
            every = simpledialog.askinteger("Recurring", "Repeat every how many days?", parent=self)
            if every:
                self.parent.recurring.append({
                    "start": d["date"],
                    "every": every,
                    "amount": d["amount"],
                    "category": d["category"],
                    "note": d["note"]
                })
                self.parent._save_recurring()
                self.destroy()


class SearchDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Search / Filter")
        self.transient(parent)
        self.grab_set()
        self.parent = parent

        frm = ttk.Frame(self, padding=10)
        frm.pack()

        ttk.Label(frm, text="From (YYYY-MM-DD)").grid(row=0, column=0)
        ttk.Label(frm, text="To (YYYY-MM-DD)").grid(row=1, column=0)
        ttk.Label(frm, text="Category").grid(row=2, column=0)
        ttk.Label(frm, text="Note contains").grid(row=3, column=0)

        self.v_from = tk.StringVar()
        self.v_to = tk.StringVar()
        self.v_cat = tk.StringVar()
        self.v_note = tk.StringVar()

        ttk.Entry(frm, textvariable=self.v_from).grid(row=0, column=1)
        ttk.Entry(frm, textvariable=self.v_to).grid(row=1, column=1)
        ttk.Combobox(frm, textvariable=self.v_cat,
                     values=[""] + parent.categories, state="readonly").grid(row=2, column=1)
        ttk.Entry(frm, textvariable=self.v_note).grid(row=3, column=1)

        ttk.Button(frm, text="Apply", command=self.apply).grid(row=4, column=1, sticky="e")
        ttk.Button(frm, text="Clear", command=self.clear).grid(row=4, column=0)

    def apply(self):
        filters = {}
        if self.v_from.get():
            f = dt.datetime.strptime(self.v_from.get(), "%Y-%m-%d").date()
            filters["from"] = lambda e: dt.date.fromisoformat(e["date"]) >= f
        if self.v_to.get():
            t = dt.datetime.strptime(self.v_to.get(), "%Y-%m-%d").date()
            filters["to"] = lambda e: dt.date.fromisoformat(e["date"]) <= t
        if self.v_cat.get():
            filters["cat"] = lambda e: e["category"] == self.v_cat.get()
        if self.v_note.get():
            pattern = re.compile(self.v_note.get(), re.I)
            filters["note"] = lambda e: pattern.search(e["note"])
        self.parent.search_filters = filters
        self.parent.refresh_tree()
        self.destroy()

    def clear(self):
        self.parent.search_filters = {}
        self.parent.refresh_tree()
        self.destroy()


class ChartsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Charts")
        self.transient(parent)
        self.grab_set()
        self.geometry("700x500")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Pie
        frm_pie = ttk.Frame(nb)
        nb.add(frm_pie, text="Pie Category")
        self.build_pie(frm_pie)

        # Bar monthly
        frm_bar = ttk.Frame(nb)
        nb.add(frm_bar, text="Bar Monthly")
        self.build_bar(frm_bar)

    def build_pie(self, parent):
        cat_total = {}
        for e in self.master.expenses:
            cat_total[e["category"]] = cat_total.get(e["category"], 0) + e["amount"]
        if not cat_total:
            ttk.Label(parent, text="No data").pack()
            return
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(cat_total.values(), labels=cat_total.keys(), autopct='%1.1f%%')
        ax.set_title("Expense by Category")
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def build_bar(self, parent):
        month_total = {}
        for e in self.master.expenses:
            m = e["date"][:7]
            month_total[m] = month_total.get(m, 0) + e["amount"]
        if not month_total:
            ttk.Label(parent, text="No data").pack()
            return
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(month_total.keys(), month_total.values())
        ax.set_title("Monthly Spending")
        ax.set_ylabel("Amount")
        plt.xticks(rotation=45)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)


# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------
if __name__ == "__main__":
    app = ExpenseManager()
    app.mainloop()