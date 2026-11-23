LIBRARY BOOK ISSUE REGISTER

Requirements: Python 3 with Tkinter (standard library only).

Run from the source folder:
    cd source
    python3 main.py

Files:
    source/main.py  - Tkinter user interface
    source/logic.py - LibraryManager class (validation, fine calculation, CSV)
    source/data/    - CSV data is created automatically when the app first runs

CSV fields: ID, Book Title, Member Name, Issue Date, Return Date, Fine, Status
Loan period: 7 days. Fine: Rs. 5 per day after the 7-day loan period.
