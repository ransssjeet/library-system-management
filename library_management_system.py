"""
Project 02: Library Management System
Bleep Assignment

This program manages books, issues and returns. It uses OOP concepts and
CSV files so the records are available the next time the program runs.
"""

import csv
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

# Keep the data folder beside this Python file.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BOOKS_FILE = DATA_DIR / "books.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"


class Book:
    """Stores information about one book."""

    def __init__(self, book_id, title, author, total_copies=1, available_copies=None):
        self.__book_id = str(book_id).strip()
        self.__title = str(title).strip()
        self.__author = str(author).strip()

        try:
            self.__total_copies = int(total_copies)
            if available_copies is None:
                self.__available_copies = self.__total_copies
            else:
                self.__available_copies = int(available_copies)
        except (TypeError, ValueError) as error:
            raise ValueError("Number of copies must be a whole number.") from error

        if not self.__book_id or not self.__title or not self.__author:
            raise ValueError("Book ID, title, and author are required.")
        if self.__total_copies < 1:
            raise ValueError("Total copies must be at least 1.")
        if not 0 <= self.__available_copies <= self.__total_copies:
            raise ValueError("Available copies must be between 0 and total copies.")

    # Properties provide controlled access to the private attributes.
    @property
    def book_id(self):
        return self.__book_id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Book title cannot be empty.")
        self.__title = value

    @property
    def author(self):
        return self.__author

    @author.setter
    def author(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Author name cannot be empty.")
        self.__author = value

    @property
    def total_copies(self):
        return self.__total_copies

    @property
    def available_copies(self):
        return self.__available_copies

    def is_available(self):
        return self.__available_copies > 0

    def add_copies(self, quantity):
        try:
            quantity = int(quantity)
        except (TypeError, ValueError) as error:
            raise ValueError("Quantity must be a whole number.") from error
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        self.__total_copies += quantity
        self.__available_copies += quantity

    def issue_one(self):
        if not self.is_available():
            raise ValueError("No copies of this book are available.")
        self.__available_copies -= 1

    def return_one(self):
        if self.__available_copies >= self.__total_copies:
            raise ValueError("All copies are already marked as available.")
        self.__available_copies += 1

    def to_dict(self):
        return {
            "book_id": self.__book_id,
            "title": self.__title,
            "author": self.__author,
            "total_copies": self.__total_copies,
            "available_copies": self.__available_copies,
        }


class FileStorage(ABC):
    """Abstract interface: any storage type must implement these methods."""

    @abstractmethod
    def load_books(self):
        pass

    @abstractmethod
    def save_books(self, books):
        pass

    @abstractmethod
    def load_transactions(self):
        pass

    @abstractmethod
    def save_transaction(self, action, book, borrower):
        pass


class CSVStorage(FileStorage):
    """Stores book and transaction records in CSV files.

    This class inherits FileStorage and implements its abstract methods.
    """

    def __init__(self, books_file=BOOKS_FILE, transactions_file=TRANSACTIONS_FILE):
        self._books_file = Path(books_file)
        self._transactions_file = Path(transactions_file)
        self._books_file.parent.mkdir(parents=True, exist_ok=True)
        self._transactions_file.parent.mkdir(parents=True, exist_ok=True)
        self._prepare_file(self._books_file, [
            "book_id", "title", "author", "total_copies", "available_copies"
        ])
        self._prepare_file(self._transactions_file, [
            "timestamp", "action", "book_id", "title", "borrower"
        ])

    @staticmethod
    def _prepare_file(path, headers):
        if not path.exists() or path.stat().st_size == 0:
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)

    def load_books(self):
        books = []
        try:
            with self._books_file.open("r", newline="", encoding="utf-8") as file:
                for row in csv.DictReader(file):
                    try:
                        books.append(Book(
                            row["book_id"],
                            row["title"],
                            row["author"],
                            row["total_copies"],
                            row["available_copies"],
                        ))
                    except (KeyError, ValueError) as error:
                        print(f"Warning: skipped an invalid book record: {error}")
        except OSError as error:
            print(f"Could not read the book file: {error}")
        return books

    def save_books(self, books):
        fieldnames = [
            "book_id", "title", "author", "total_copies", "available_copies"
        ]
        try:
            with self._books_file.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for book in books:
                    writer.writerow(book.to_dict())
        except OSError as error:
            raise RuntimeError(f"Could not save books: {error}") from error

    def load_transactions(self):
        try:
            with self._transactions_file.open("r", newline="", encoding="utf-8") as file:
                return list(csv.DictReader(file))
        except OSError as error:
            print(f"Could not read transaction history: {error}")
            return []

    def save_transaction(self, action, book, borrower):
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "book_id": book.book_id,
            "title": book.title,
            "borrower": borrower,
        }
        try:
            with self._transactions_file.open("a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["timestamp", "action", "book_id", "title", "borrower"],
                )
                writer.writerow(row)
        except OSError as error:
            raise RuntimeError(f"Could not save transaction: {error}") from error


class Library:
    """Contains the library rules and operations."""

    def __init__(self, storage):
        self._storage = storage
        self._books = {}
        for book in self._storage.load_books():
            self._books[book.book_id] = book

    def add_book(self, book_id, title, author, quantity):
        book_id = str(book_id).strip()
        if not book_id or not str(title).strip() or not str(author).strip():
            raise ValueError("Book ID, title, and author are required.")

        if book_id in self._books:
            book = self._books[book_id]
            # Avoid accidentally changing the identity of an existing book ID.
            if book.title.lower() != str(title).strip().lower():
                raise ValueError("This ID already belongs to a different title.")
            book.add_copies(quantity)
        else:
            book = Book(book_id, title, author, quantity)
            self._books[book_id] = book

        self._storage.save_books(self._books.values())
        return book

    def search_books(self, search_text):
        search_text = str(search_text).strip().lower()
        return [
            book for book in self._books.values()
            if search_text in book.book_id.lower()
            or search_text in book.title.lower()
            or search_text in book.author.lower()
        ]

    def get_book(self, book_id):
        book = self._books.get(str(book_id).strip())
        if book is None:
            raise ValueError("Book ID was not found.")
        return book

    def issue_book(self, book_id, borrower):
        borrower = str(borrower).strip()
        if not borrower:
            raise ValueError("Borrower's name is required.")
        book = self.get_book(book_id)
        book.issue_one()
        try:
            self._storage.save_books(self._books.values())
            self._storage.save_transaction("ISSUE", book, borrower)
        except RuntimeError:
            # Restore the in-memory count if saving fails.
            book.return_one()
            raise
        return book

    def return_book(self, book_id, borrower):
        borrower = str(borrower).strip()
        if not borrower:
            raise ValueError("Borrower's name is required.")
        book = self.get_book(book_id)

        # Check the saved history to ensure this borrower has an unreturned copy.
        outstanding = 0
        for transaction in self._storage.load_transactions():
            same_book = transaction.get("book_id", "") == book.book_id
            same_borrower = transaction.get("borrower", "").strip().lower() == borrower.lower()
            if same_book and same_borrower:
                if transaction.get("action") == "ISSUE":
                    outstanding += 1
                elif transaction.get("action") == "RETURN":
                    outstanding -= 1

        if outstanding <= 0:
            raise ValueError("No outstanding issue was found for this borrower and book.")

        book.return_one()
        try:
            self._storage.save_books(self._books.values())
            self._storage.save_transaction("RETURN", book, borrower)
        except RuntimeError:
            book.issue_one()
            raise
        return book

    def all_books(self, available_only=False):
        books = list(self._books.values())
        if available_only:
            books = [book for book in books if book.is_available()]
        return sorted(books, key=lambda item: item.book_id.lower())

    def transaction_history(self):
        return self._storage.load_transactions()


class LibraryManagementSystem:
    """Handles the console menu and user input."""

    def __init__(self, library):
        self._library = library

    @staticmethod
    def ask_required(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Please enter a value. This field cannot be empty.")

    @staticmethod
    def show_books(books):
        if not books:
            print("\nNo books found.")
            return

        print("\n" + "-" * 78)
        print(f"{'ID':<10}{'TITLE':<28}{'AUTHOR':<22}{'TOTAL':>8}{'AVAILABLE':>10}")
        print("-" * 78)
        for book in books:
            print(
                f"{book.book_id:<10}"
                f"{book.title[:26]:<28}"
                f"{book.author[:20]:<22}"
                f"{book.total_copies:>8}"
                f"{book.available_copies:>10}"
            )
        print("-" * 78)

    def run(self):
        while True:
            print("\n========== LIBRARY MANAGEMENT SYSTEM ==========")
            print("1. Add book")
            print("2. Search books")
            print("3. Issue book")
            print("4. Return book")
            print("5. Display all books")
            print("6. Display available books")
            print("7. Display transaction history")
            print("0. Exit")

            choice = input("Enter your choice: ").strip()

            try:
                if choice == "1":
                    book_id = self.ask_required("Book ID: ")
                    title = self.ask_required("Book title: ")
                    author = self.ask_required("Author: ")
                    quantity = self.ask_required("Number of copies: ")
                    book = self._library.add_book(book_id, title, author, quantity)
                    print(f"Saved book: {book.title} (ID: {book.book_id}).")

                elif choice == "2":
                    search_text = self.ask_required("Search by ID, title, or author: ")
                    self.show_books(self._library.search_books(search_text))

                elif choice == "3":
                    book_id = self.ask_required("Book ID to issue: ")
                    borrower = self.ask_required("Borrower's name: ")
                    book = self._library.issue_book(book_id, borrower)
                    print(f"'{book.title}' issued to {borrower}.")

                elif choice == "4":
                    book_id = self.ask_required("Book ID to return: ")
                    borrower = self.ask_required("Borrower's name: ")
                    book = self._library.return_book(book_id, borrower)
                    print(f"'{book.title}' returned by {borrower}.")

                elif choice == "5":
                    self.show_books(self._library.all_books())

                elif choice == "6":
                    self.show_books(self._library.all_books(available_only=True))

                elif choice == "7":
                    transactions = self._library.transaction_history()
                    if not transactions:
                        print("\nNo transactions recorded yet.")
                    else:
                        print("\nTRANSACTION HISTORY")
                        print("-" * 90)
                        for item in transactions:
                            print(
                                f"{item.get('timestamp', '')} | "
                                f"{item.get('action', ''):<6} | "
                                f"{item.get('book_id', '')} | "
                                f"{item.get('title', '')} | "
                                f"Borrower: {item.get('borrower', '')}"
                            )
                        print("-" * 90)

                elif choice == "0":
                    print("Records are saved. Thank you for using the Library Management System.")
                    break

                else:
                    print("Invalid choice. Please enter a number from 0 to 7.")

            except ValueError as error:
                print(f"Could not complete the action: {error}")
            except RuntimeError as error:
                print(f"File operation failed: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nProgram stopped.")
                break


def main():
    """Create the objects and start the application."""
    storage = CSVStorage()
    library = Library(storage)
    app = LibraryManagementSystem(library)
    app.run()


if __name__ == "__main__":
    main()
