# Project 02 — Library Management System

## About
This is a console-based Library Management System made with Python. It allows a user to add books, search for books, issue and return books, display available books, and view transaction history.

## Features
- Add a new book or add more copies to an existing book
- Search by book ID, title, or author
- Issue books to borrowers
- Return books after checking the issue history
- Display all books and currently available books
- Save inventory and transaction records in CSV files
- Handle invalid input and file errors

## OOP concepts demonstrated
1. **Classes and objects:** `Book`, `CSVStorage`, `Library`, and `LibraryManagementSystem`.
2. **Encapsulation:** `Book` uses private attributes such as `__title` and properties to control access. The other classes use protected-style attributes such as `_books` and `_storage`.
3. **Inheritance:** `CSVStorage` inherits from `FileStorage`.
4. **Abstraction:** `FileStorage` is an abstract base class using `ABC` and `@abstractmethod`.
5. **File handling:** The program reads and writes `data/books.csv` and `data/transactions.csv`.
6. **Exception handling:** `try`/`except` blocks handle invalid quantities and file errors.

## Requirements
- Python 3.10 or newer recommended
- No third-party packages required

## How to run
1. Extract the ZIP file.
2. Open the extracted folder in a terminal or VS Code.
3. Run:

   ```bash
   python library_management_system.py
   ```

   On some Windows systems, use `py library_management_system.py`.

## Example test
1. Choose `1` and add ID `B001`, title `Python Basics`, author `A. Author`, quantity `2`.
2. Choose `5` to display all books.
3. Choose `3` and issue `B001` to `Sam`.
4. Choose `6` to check the available count.
5. Choose `4` and return `B001` from `Sam`.
6. Choose `7` to see the transaction history.
7. Exit and run the program again to check that records remain saved.

## Files
- `library_management_system.py`: application source code
- `data/books.csv`: inventory records
- `data/transactions.csv`: issue/return history
- `README.md`: project details and run instructions
- `OOP_CONCEPTS.md`: a short explanation of the OOP concepts

Please run the program and understand the methods before submitting it.
