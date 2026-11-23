"""Tkinter user interface for the Library Book Issue Register."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from logic import LibraryManager


class LibraryApp:
    """Build the interface and connect widgets to LibraryManager."""

    def __init__(self, root):
        """Create widgets and display saved records."""
        self.root = root
        self.manager = LibraryManager()
        root.title("Library Book Issue Register")
        root.geometry("900x620")
        root.minsize(700, 500)
        root.configure(bg="#f2f5f9")
        tk.Label(root, text="LIBRARY BOOK ISSUE REGISTER", font=("Arial", 18, "bold"),
                 bg="#172b4d", fg="white", pady=14).pack(fill="x")

        form = ttk.LabelFrame(root, text="Issue a book", padding=10)
        form.pack(fill="x", padx=14, pady=10)
        self.title_entry = self.add_field(form, "Book title", 0)
        self.member_entry = self.add_field(form, "Member name", 1)
        self.date_entry = self.add_field(form, "Issue date (YYYY-MM-DD)", 2)
        self.date_entry.insert(0, date.today().isoformat())
        ttk.Button(form, text="Issue Book", command=self.issue).grid(row=0, column=6, rowspan=2, padx=12)

        search = ttk.Frame(root, padding=(14, 0))
        search.pack(fill="x")
        ttk.Label(search, text="Search member:").pack(side="left")
        self.search_entry = ttk.Entry(search, width=25)
        self.search_entry.pack(side="left", padx=6)
        ttk.Button(search, text="Search", command=self.search).pack(side="left")
        ttk.Button(search, text="Show All", command=self.show_all).pack(side="left", padx=5)
        ttk.Button(search, text="Return Selected", command=self.return_book).pack(side="right")

        area = ttk.Frame(root, padding=14)
        area.pack(fill="both", expand=True)
        columns = LibraryManager.FIELDS
        self.table = ttk.Treeview(area, columns=columns, show="headings", height=13)
        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=115, anchor="center")
        self.table.column("Book Title", width=170)
        self.table.column("Member Name", width=150)
        ybar = ttk.Scrollbar(area, orient="vertical", command=self.table.yview)
        xbar = ttk.Scrollbar(area, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        self.summary = ttk.Label(root, padding=10, font=("Arial", 10, "bold"))
        self.summary.pack(fill="x")
        self.refresh_table()

    def add_field(self, parent, label, column):
        """Create a labeled entry field."""
        ttk.Label(parent, text=label).grid(row=0, column=column * 2, sticky="w", padx=4)
        entry = ttk.Entry(parent, width=19)
        entry.grid(row=1, column=column * 2, padx=4, pady=5)
        return entry

    def refresh_table(self, records=None):
        """Refresh the visible records and dashboard counts. # FR4"""
        self.table.delete(*self.table.get_children())
        for row in self.manager.records if records is None else records:
            self.table.insert("", "end", values=[row[key] for key in LibraryManager.FIELDS])
        counts = self.manager.get_summary()
        self.summary.config(text="   |   ".join(f"{key}: {value}" for key, value in counts.items()))

    def issue(self):
        """Validate form data and issue a book, reporting errors safely. # FR1"""
        try:
            self.manager.issue_book(self.title_entry.get(), self.member_entry.get(), self.date_entry.get())
            self.title_entry.delete(0, "end")
            self.member_entry.delete(0, "end")
            self.refresh_table()
            messagebox.showinfo("Success", "Book issued successfully.")
        except (ValueError, OSError) as error:
            messagebox.showerror("Input / File Error", str(error))

    def return_book(self):
        """Return the selected record and display its fine. # FR2 # FR3"""
        selected = self.table.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Select a book record first.")
            return
        record_id = self.table.item(selected[0], "values")[0]
        try:
            record = self.manager.return_book(record_id)
            self.refresh_table()
            messagebox.showinfo("Book Returned", f"Book returned. Fine: Rs. {record['Fine']}")
        except (ValueError, OSError) as error:
            messagebox.showerror("Return Error", str(error))

    def search(self):
        """Search records by member name. # FR5"""
        query = self.search_entry.get()
        if not query.strip():
            messagebox.showerror("Search Error", "Enter a member name to search.")
            return
        self.refresh_table(self.manager.search_member(query))

    def show_all(self):
        """Display every saved record."""
        self.search_entry.delete(0, "end")
        self.refresh_table()


def main():
    """Start the Tkinter application."""
    root = tk.Tk()
    LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
