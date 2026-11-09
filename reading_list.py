import json
import csv
import os


class ReadingListManager:

    def __init__(self, filename="favourites.json"):
        self.filename = filename

    # Load saved books
    def load_books(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                return json.load(file)

        return []

    # Save books
    def save_books(self, books):
        with open(self.filename, "w") as file:
            json.dump(books, file, indent=4)

    # Add a book to favourites
    def add_book(self, book):
        books = self.load_books()
        books.append(book)
        self.save_books(books)

    # Export books to CSV
    def export_to_csv(self, csv_filename="reading_list.csv"):
        books = self.load_books()

        if not books:
            print("Your reading list is empty.")
            return

        with open(csv_filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=books[0].keys())

            writer.writeheader()
            writer.writerows(books)

        print("Reading list exported to CSV successfully!")