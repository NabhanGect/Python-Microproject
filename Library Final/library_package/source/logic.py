"""Business logic for the Library Book Issue Register."""
import csv
import os
from datetime import datetime, date


class LibraryManager:
    """Validate, process, and store library issue records."""

    FIELDS = ["ID", "Book Title", "Member Name", "Issue Date", "Return Date", "Fine", "Status"]
    LOAN_DAYS = 7
    FINE_PER_DAY = 5

    def __init__(self, file_path=None):
        """Set the CSV location and load existing records."""
        base = os.path.dirname(__file__)
        self.file_path = file_path or os.path.join(base, "data", "library_records.csv")
        self.records = []
        self.load_records()

    def load_records(self):
        """Load records; create the CSV with headers if it is missing. # FR4"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            with open(self.file_path, "r", newline="", encoding="utf-8") as file:
                self.records = list(csv.DictReader(file))
        except FileNotFoundError:
            self.records = []
            self.save_records()
        return self.records

    def save_records(self):
        """Write all in-memory records to CSV. # FR4"""
        try:
            with open(self.file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                writer.writeheader()
                writer.writerows(self.records)
        except OSError as error:
            raise ValueError(f"Could not save records: {error}") from error

    def validate_issue(self, title, member, issue_date):
        """Validate book details and the YYYY-MM-DD issue date. # FR1"""
        title, member = title.strip(), member.strip()
        if not title or not member:
            raise ValueError("Book title and member name are required.")
        try:
            parsed = datetime.strptime(issue_date.strip(), "%Y-%m-%d").date()
        except ValueError as error:
            raise ValueError("Issue date must use YYYY-MM-DD.") from error
        if parsed > date.today():
            raise ValueError("Issue date cannot be in the future.")
        return title, member, parsed

    def issue_book(self, title, member, issue_date):
        """Add a new issued book record. # FR1"""
        title, member, parsed = self.validate_issue(title, member, issue_date)
        next_id = max([int(row["ID"]) for row in self.records] or [0]) + 1
        record = {"ID": str(next_id), "Book Title": title, "Member Name": member,
                  "Issue Date": parsed.isoformat(), "Return Date": "", "Fine": "0", "Status": "Issued"}
        self.records.append(record)
        self.save_records()
        return record

    def return_book(self, record_id, return_date=None):
        """Return an issued book and calculate any late fine. # FR2 # FR3"""
        try:
            returned = datetime.strptime((return_date or date.today().isoformat()), "%Y-%m-%d").date()
            index = next(i for i, row in enumerate(self.records) if row["ID"] == str(record_id))
        except (ValueError, StopIteration) as error:
            raise ValueError("Select a valid record and use a valid return date (YYYY-MM-DD).") from error
        row = self.records[index]
        if row["Status"] != "Issued":
            raise ValueError("This book has already been returned.")
        issued = datetime.strptime(row["Issue Date"], "%Y-%m-%d").date()
        if returned < issued:
            raise ValueError("Return date cannot be before the issue date.")
        fine = max(0, (returned - issued).days - self.LOAN_DAYS) * self.FINE_PER_DAY
        row.update({"Return Date": returned.isoformat(), "Fine": str(fine), "Status": "Returned"})
        self.save_records()
        return row

    def search_member(self, query):
        """Return records whose member name contains the query. # FR5"""
        term = query.strip().lower()
        return [row for row in self.records if term in row["Member Name"].lower()]

    def get_summary(self):
        """Return total, issued, returned, and overdue counts. # FR4"""
        today = date.today()
        overdue = sum(1 for row in self.records if row["Status"] == "Issued" and
                      (today - datetime.strptime(row["Issue Date"], "%Y-%m-%d").date()).days > self.LOAN_DAYS)
        return {"Total": len(self.records), "Issued": sum(r["Status"] == "Issued" for r in self.records),
                "Returned": sum(r["Status"] == "Returned" for r in self.records), "Overdue": overdue}
