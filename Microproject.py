import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime, date

# ---------------- CONFIGURATION ----------------

FILE = "library_records.csv"
LOAN_DAYS = 7
FINE_PER_DAY = 5

FIELDS = [
    "ID", "Book Title", "Member Name",
    "Issue Date", "Return Date", "Fine", "Status"
]


# ---------------- FILE HANDLING ----------------

def load_records():
    if not os.path.exists(FILE):
        with open(FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

    with open(FILE, "r", newline="") as f:
        return list(csv.DictReader(f))


def save_records(records):
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("Library Book Issue Register")
root.geometry("1050x650")
root.configure(bg="#eaf2f8")

records = load_records()


# ---------------- TITLE ----------------

title = tk.Label(
    root,
    text="LIBRARY BOOK ISSUE REGISTER",
    font=("Arial", 22, "bold"),
    bg="#154360",
    fg="white",
    pady=15
)
title.pack(fill="x")


# ---------------- INPUT SECTION ----------------

form = tk.Frame(root, bg="#eaf2f8", pady=15)
form.pack()

tk.Label(
    form, text="Book Title:",
    font=("Arial", 12), bg="#eaf2f8"
).grid(row=0, column=0, padx=10, pady=10)

book_entry = tk.Entry(form, font=("Arial", 12), width=25)
book_entry.grid(row=0, column=1, padx=10)

tk.Label(
    form, text="Member Name:",
    font=("Arial", 12), bg="#eaf2f8"
).grid(row=1, column=0, padx=10, pady=10)

member_entry = tk.Entry(form, font=("Arial", 12), width=25)
member_entry.grid(row=1, column=1, padx=10)

tk.Label(
    form, text="Issue Date:",
    font=("Arial", 12), bg="#eaf2f8"
).grid(row=2, column=0, padx=10, pady=10)

date_entry = tk.Entry(form, font=("Arial", 12), width=25)
date_entry.grid(row=2, column=1, padx=10)

date_entry.insert(0, date.today().isoformat())


# ---------------- TABLE SECTION ----------------

table_frame = tk.Frame(root)
table_frame.pack(padx=15, pady=10, fill="both", expand=True)

columns = (
    "ID", "Book", "Member",
    "Issue Date", "Return Date", "Fine", "Status"
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=12
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=135, anchor="center")

tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)
scrollbar.pack(side="right", fill="y")

tree.configure(yscrollcommand=scrollbar.set)


# ---------------- REFRESH TABLE ----------------

def refresh_table(data=None):

    for row in tree.get_children():
        tree.delete(row)

    if data is None:
        data = records

    for record in data:
        tree.insert(
            "",
            "end",
            values=(
                record["ID"],
                record["Book Title"],
                record["Member Name"],
                record["Issue Date"],
                record["Return Date"],
                record["Fine"],
                record["Status"]
            )
        )

    update_dashboard()


# ---------------- DASHBOARD ----------------

dashboard = tk.Label(
    root,
    font=("Arial", 12, "bold"),
    bg="#eaf2f8",
    fg="#154360"
)
dashboard.pack(pady=8)


def update_dashboard():

    issued = sum(
        1 for r in records if r["Status"] == "Issued"
    )

    returned = sum(
        1 for r in records if r["Status"] == "Returned"
    )

    overdue = 0

    for r in records:
        if r["Status"] == "Issued":
            issue_date = datetime.strptime(
                r["Issue Date"], "%Y-%m-%d"
            ).date()

            if (date.today() - issue_date).days > LOAN_DAYS:
                overdue += 1

    dashboard.config(
        text=f"Total Issued: {issued}     "
             f"Returned: {returned}     "
             f"Overdue: {overdue}"
    )


# ---------------- ISSUE BOOK ----------------

def issue_book():

    book = book_entry.get().strip()
    member = member_entry.get().strip()
    issue_date = date_entry.get().strip()

    if not book or not member or not issue_date:
        messagebox.showerror(
            "Error", "Please fill all the fields!"
        )
        return

    try:
        datetime.strptime(issue_date, "%Y-%m-%d")

        if datetime.strptime(issue_date, "%Y-%m-%d").date() > date.today():
            messagebox.showerror(
                "Error", "Issue date cannot be in the future!"
            )
            return

    except ValueError:
        messagebox.showerror(
            "Error", "Enter date in YYYY-MM-DD format!"
        )
        return

    new_id = max(
        [int(r["ID"]) for r in records],
        default=0
    ) + 1

    record = {
        "ID": str(new_id),
        "Book Title": book,
        "Member Name": member,
        "Issue Date": issue_date,
        "Return Date": "",
        "Fine": "0",
        "Status": "Issued"
    }

    records.append(record)
    save_records(records)

    refresh_table()

    book_entry.delete(0, tk.END)
    member_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    date_entry.insert(0, date.today().isoformat())

    messagebox.showinfo(
        "Success", "Book issued successfully!"
    )


# ---------------- RETURN BOOK ----------------

def return_book():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Warning", "Please select a book to return!"
        )
        return

    item = tree.item(selected[0])
    selected_id = item["values"][0]

    for record in records:

        if record["ID"] == str(selected_id):

            if record["Status"] == "Returned":
                messagebox.showwarning(
                    "Warning", "This book is already returned!"
                )
                return

            issue = datetime.strptime(
                record["Issue Date"], "%Y-%m-%d"
            ).date()

            return_date = date.today()

            days = (return_date - issue).days

            late_days = max(0, days - LOAN_DAYS)

            fine = late_days * FINE_PER_DAY

            record["Return Date"] = return_date.isoformat()
            record["Fine"] = str(fine)
            record["Status"] = "Returned"

            save_records(records)
            refresh_table()

            messagebox.showinfo(
                "Book Returned",
                f"Book returned successfully!\n\n"
                f"Borrowing Days: {days}\n"
                f"Late Days: {late_days}\n"
                f"Fine Amount: Rs. {fine}"
            )
            return


# ---------------- SEARCH BY MEMBER ----------------

def search_member():

    name = search_entry.get().strip().lower()

    if not name:
        messagebox.showwarning(
            "Warning", "Enter member name to search!"
        )
        return

    result = [
        r for r in records
        if name in r["Member Name"].lower()
    ]

    refresh_table(result)

    if not result:
        messagebox.showinfo(
            "Search", "No records found!"
        )


def show_all():
    search_entry.delete(0, tk.END)
    refresh_table()


# ---------------- BUTTON SECTION ----------------

button_frame = tk.Frame(root, bg="#eaf2f8")
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="ISSUE BOOK",
    command=issue_book,
    bg="#229954",
    fg="white",
    font=("Arial", 11, "bold"),
    width=15
).grid(row=0, column=0, padx=10)

tk.Button(
    button_frame,
    text="RETURN BOOK",
    command=return_book,
    bg="#2874a6",
    fg="white",
    font=("Arial", 11, "bold"),
    width=15
).grid(row=0, column=1, padx=10)


# ---------------- SEARCH SECTION ----------------

search_frame = tk.Frame(root, bg="#eaf2f8")
search_frame.pack(pady=12)

tk.Label(
    search_frame,
    text="Search Member:",
    font=("Arial", 12),
    bg="#eaf2f8"
).grid(row=0, column=0, padx=5)

search_entry = tk.Entry(
    search_frame,
    font=("Arial", 12),
    width=22
)
search_entry.grid(row=0, column=1, padx=5)

tk.Button(
    search_frame,
    text="SEARCH",
    command=search_member,
    bg="#8e44ad",
    fg="white",
    width=12
).grid(row=0, column=2, padx=5)

tk.Button(
    search_frame,
    text="SHOW ALL",
    command=show_all,
    bg="#566573",
    fg="white",
    width=12
).grid(row=0, column=3, padx=5)


# ---------------- START APPLICATION ----------------

refresh_table()

root.mainloop()
