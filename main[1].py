import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import csv

from database import (
    initialize_database, verify_login, add_waste_record,
    get_waste_records, delete_waste_record, get_summary
)

# EcoTrack starter application: Login + Dashboard + Waste Entry + Records + Reports
BG = "#F1F7F2"
GREEN = "#176B45"
DARK = "#124B33"
LIGHT_GREEN = "#DDF2E4"
WHITE = "#FFFFFF"
TEXT = "#20352A"
MUTED = "#64756B"
CATEGORIES = {
    "Organic": True,
    "Paper": True,
    "Plastic": True,
    "Metal": True,
    "Glass": True,
    "E-waste": False,
    "Mixed / Other": False,
}

class EcoTrackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EcoTrack | Smart Waste Management")
        self.root.geometry("1050x680")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()
        initialize_database()
        self.show_login()

    def configure_styles(self):
        self.style.configure("Treeview", rowheight=30, font=("Segoe UI", 10),
                             background=WHITE, fieldbackground=WHITE, foreground=TEXT)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                             background=LIGHT_GREEN, foreground=DARK)
        self.style.map("Treeview", background=[("selected", "#B9E4C8")])
        self.style.configure("TCombobox", padding=7)
        self.style.configure("TEntry", padding=7)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        card = tk.Frame(outer, bg=WHITE, padx=42, pady=35,
                        highlightthickness=1, highlightbackground="#D7E7DA")
        card.place(relx=0.5, rely=0.5, anchor="center", width=410, height=430)

        tk.Label(card, text="🌱", font=("Segoe UI Emoji", 34), bg=WHITE).pack(pady=(3, 0))
        tk.Label(card, text="EcoTrack", font=("Segoe UI", 25, "bold"),
                 fg=GREEN, bg=WHITE).pack()
        tk.Label(card, text="SMART WASTE MANAGEMENT", font=("Segoe UI", 9, "bold"),
                 fg=MUTED, bg=WHITE).pack(pady=(0, 25))

        tk.Label(card, text="Username", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        username = ttk.Entry(card, font=("Segoe UI", 11))
        username.pack(fill="x", pady=(6, 16))
        username.insert(0, "admin")

        tk.Label(card, text="Password", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        password = ttk.Entry(card, show="*", font=("Segoe UI", 11))
        password.pack(fill="x", pady=(6, 20))
        password.insert(0, "EcoTrack@123")

        def login():
            if verify_login(username.get(), password.get()):
                self.show_dashboard()
            else:
                messagebox.showerror("Login failed", "Incorrect username or password.")

        tk.Button(card, text="LOGIN", command=login, bg=GREEN, fg=WHITE,
                  activebackground=DARK, activeforeground=WHITE, relief="flat",
                  font=("Segoe UI", 11, "bold"), cursor="hand2").pack(fill="x", ipady=9)
        tk.Label(card, text="Demo login: admin  |  EcoTrack@123",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(pady=18)
        password.bind("<Return>", lambda _event: login())
        username.focus_set()

    def show_dashboard(self):
        self.clear()
        header = tk.Frame(self.root, bg=DARK, height=76)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🌱  EcoTrack", bg=DARK, fg=WHITE,
                 font=("Segoe UI", 21, "bold")).pack(side="left", padx=25)
        tk.Label(header, text="SMART WASTE MANAGEMENT SYSTEM", bg=DARK, fg="#D4EBDD",
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=12, pady=(9, 0))
        tk.Button(header, text="Log out", command=self.show_login, bg="#2B7654",
                  fg=WHITE, relief="flat", padx=16, pady=7, cursor="hand2").pack(side="right", padx=22)

        body = tk.Frame(self.root, bg=BG, padx=26, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Dashboard Overview", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(body, text="Record, monitor and understand your waste collection.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 17))

        cards = tk.Frame(body, bg=BG)
        cards.pack(fill="x")
        self.summary_labels = {}
        card_specs = [
            ("Total waste", "total", "kg"),
            ("Recyclable", "recyclable", "kg"),
            ("Non-recyclable", "non_recyclable", "kg"),
            ("Collection records", "records", ""),
        ]
        for title, key, suffix in card_specs:
            box = tk.Frame(cards, bg=WHITE, padx=17, pady=15,
                           highlightthickness=1, highlightbackground="#DCE9DE")
            box.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Label(box, text=title, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            value = tk.Label(box, text="0", bg=WHITE, fg=GREEN,
                             font=("Segoe UI", 21, "bold"))
            value.pack(anchor="w", pady=(8, 0))
            self.summary_labels[key] = (value, suffix)

        nav = tk.Frame(body, bg=BG)
        nav.pack(fill="x", pady=23)
        tk.Label(nav, text="Quick actions", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 10))
        actions = [
            ("＋  Add waste record", self.show_add_record),
            ("▤  View records", self.show_records),
            ("▥  Reports & analytics", self.show_reports),
        ]
        for label, command in actions:
            tk.Button(nav, text=label, command=command, bg=GREEN, fg=WHITE,
                      activebackground=DARK, activeforeground=WHITE, relief="flat",
                      font=("Segoe UI", 10, "bold"), padx=18, pady=13,
                      cursor="hand2").pack(side="left", padx=(0, 12))

        tip = tk.Frame(body, bg=LIGHT_GREEN, padx=18, pady=15)
        tip.pack(fill="x", pady=(2, 0))
        tk.Label(tip, text="♻  Eco tip", bg=LIGHT_GREEN, fg=DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(tip, text="Keep paper, plastic, glass and metal separate where local collection rules allow.",
                 bg=LIGHT_GREEN, fg=TEXT, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
        self.refresh_summary()

    def refresh_summary(self):
        totals, _ = get_summary()
        for key, (label, suffix) in self.summary_labels.items():
            value = totals[key]
            display = f"{value:.1f} {suffix}".strip() if key != "records" else str(value)
            label.config(text=display)

    def page_header(self, title):
        top = tk.Frame(self.root, bg=DARK, padx=22, pady=15)
        top.pack(fill="x")
        tk.Label(top, text="🌱 EcoTrack", bg=DARK, fg=WHITE,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(top, text="← Dashboard", command=self.show_dashboard, bg="#2B7654",
                  fg=WHITE, relief="flat", padx=12, pady=6).pack(side="right")
        tk.Label(self.root, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w", padx=27, pady=(22, 12))

    def show_add_record(self):
        self.clear()
        self.page_header("Add Waste Record")
        form = tk.Frame(self.root, bg=WHITE, padx=28, pady=24,
                        highlightthickness=1, highlightbackground="#DCE9DE")
        form.pack(fill="x", padx=27, pady=5)

        fields = {}
        def add_field(label, key, widget="entry", values=None, default=""):
            tk.Label(form, text=label, bg=WHITE, fg=TEXT,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(9, 4))
            if widget == "combo":
                control = ttk.Combobox(form, values=values, state="readonly", font=("Segoe UI", 10))
                control.set(default or values[0])
            else:
                control = ttk.Entry(form, font=("Segoe UI", 10))
                control.insert(0, default)
            control.pack(fill="x", ipady=3)
            fields[key] = control

        add_field("Waste category", "category", "combo", list(CATEGORIES.keys()), "Organic")
        add_field("Quantity (kg)", "quantity", default="1")
        add_field("Collection date (YYYY-MM-DD)", "date", default=date.today().isoformat())
        add_field("Collection location", "location", default="College Campus")
        add_field("Notes (optional)", "notes", default="")

        def save():
            category = fields["category"].get()
            quantity_text = fields["quantity"].get().strip()
            date_text = fields["date"].get().strip()
            location = fields["location"].get().strip()
            notes = fields["notes"].get().strip()
            try:
                quantity = float(quantity_text)
                if quantity <= 0:
                    raise ValueError
                date.fromisoformat(date_text)
                if not location:
                    raise ValueError("location")
            except ValueError as exc:
                messagebox.showerror("Invalid input",
                    "Enter a quantity greater than zero, a valid date (YYYY-MM-DD), and a location.")
                return
            add_waste_record(category, quantity, date_text, location,
                             CATEGORIES[category], notes)
            messagebox.showinfo("Saved", "Waste record added successfully.")
            self.show_dashboard()

        buttons = tk.Frame(self.root, bg=BG)
        buttons.pack(anchor="w", padx=27, pady=18)
        tk.Button(buttons, text="Save record", command=save, bg=GREEN, fg=WHITE,
                  relief="flat", padx=22, pady=10, font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Button(buttons, text="Cancel", command=self.show_dashboard, bg="#E2EAE4",
                  fg=TEXT, relief="flat", padx=22, pady=10).pack(side="left", padx=10)

    def show_records(self):
        self.clear()
        self.page_header("Waste Records")
        container = tk.Frame(self.root, bg=BG, padx=25)
        container.pack(fill="both", expand=True)
        columns = ("id", "category", "quantity", "date", "location", "recyclable")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        headings = {
            "id": "ID", "category": "Category", "quantity": "Quantity (kg)",
            "date": "Date", "location": "Location", "recyclable": "Recyclable"
        }
        widths = {"id": 55, "category": 140, "quantity": 120, "date": 120,
                  "location": 220, "recyclable": 120}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        tree.pack(fill="both", expand=True, pady=8)

        for row in get_waste_records():
            tree.insert("", "end", values=(
                row["id"], row["category"], f'{row["quantity"]:.2f}',
                row["collection_date"], row["location"],
                "Yes" if row["recyclable"] else "No"
            ))

        def remove_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select record", "Please select a record to delete.")
                return
            record_id = tree.item(selected[0], "values")[0]
            if messagebox.askyesno("Confirm delete", f"Delete record #{record_id}?"):
                delete_waste_record(record_id)
                self.show_records()

        tk.Button(container, text="Delete selected record", command=remove_selected,
                  bg="#B84040", fg=WHITE, relief="flat", padx=16, pady=9).pack(anchor="w", pady=10)

    def show_reports(self):
        self.clear()
        self.page_header("Reports & Analytics")
        body = tk.Frame(self.root, bg=BG, padx=27)
        body.pack(fill="both", expand=True)
        totals, categories = get_summary()
        total = float(totals["total"])
        recyclable = float(totals["recyclable"])
        percent = (recyclable / total * 100) if total else 0

        report = tk.Frame(body, bg=WHITE, padx=22, pady=20,
                          highlightthickness=1, highlightbackground="#DCE9DE")
        report.pack(fill="x", pady=5)
        tk.Label(report, text="Waste Summary", bg=WHITE, fg=GREEN,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        summary_text = (
            f"Total waste recorded: {total:.2f} kg\n"
            f"Recyclable waste: {recyclable:.2f} kg\n"
            f"Non-recyclable waste: {float(totals['non_recyclable']):.2f} kg\n"
            f"Recyclable share: {percent:.1f}%\n"
            f"Number of records: {totals['records']}"
        )
        tk.Label(report, text=summary_text, bg=WHITE, fg=TEXT, justify="left",
                 font=("Segoe UI", 11), line spacing=8).pack(anchor="w", pady=12)

        tk.Label(body, text="Category-wise totals", bg=BG, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15, 5))
        for item in categories:
            tk.Label(body, text=f"• {item['category']}: {item['quantity']:.2f} kg",
                     bg=BG, fg=TEXT, font=("Segoe UI", 10)).pack(anchor="w", pady=2)

        def export_csv():
            path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                initialfile="ecotrack_waste_report.csv"
            )
            if not path:
                return
            rows = get_waste_records()
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Category", "Quantity (kg)", "Date",
                                 "Location", "Recyclable", "Notes"])
                for row in rows:
                    writer.writerow([
                        row["id"], row["category"], row["quantity"],
                        row["collection_date"], row["location"],
                        "Yes" if row["recyclable"] else "No", row["notes"]
                    ])
            messagebox.showinfo("Export complete", f"Report saved to:\n{path}")

        tk.Button(body, text="Export records to CSV", command=export_csv,
                  bg=GREEN, fg=WHITE, relief="flat", padx=18, pady=10).pack(anchor="w", pady=18)


if __name__ == "__main__":
    root = tk.Tk()
    app = EcoTrackApp(root)
    root.mainloop()
