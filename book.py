from utils import clean_isbn


class Book:

    # Constructor: Initialise book attributes
    def __init__(self, title, authors, isbn=None,
                 first_publish_year=None, subjects=None,
                 page_count=None, cover_image=None):

        self.title = title
        self.authors = authors
        self.isbn = isbn
        self.first_publish_year = first_publish_year
        self.subjects = subjects
        self.page_count = page_count
        self.cover_image = cover_image

    # Display book information
    def display_info(self):

        print("\n----- BOOK INFORMATION -----")

        print(f"Title: {self.title}")
        print(f"Author(s): {', '.join(self.authors)}")
        print(f"ISBN: {self.isbn or 'Not available'}")
        print(f"Publication Year: {self.first_publish_year or 'Not available'}")
        print(f"Subjects: {', '.join(self.subjects or []) or 'Not available'}")
        print(f"Page Count: {self.page_count or 'Not available'}")

        print("----------------------------")

    # Validate ISBN-10 and ISBN-13
    def validate_isbn(self):

        isbn = clean_isbn(self.isbn)

        if not isbn:
            return False

        # Validate ISBN-10
        if len(isbn) == 10:

            total = 0

            for index, character in enumerate(isbn):

                if character == "X" and index == 9:
                    digit = 10

                elif character.isdigit():
                    digit = int(character)

                else:
                    return False

                total += digit * (10 - index)

            return total % 11 == 0

        # Validate ISBN-13
        elif len(isbn) == 13:

            if not isbn.isdigit():
                return False

            total = 0

            for index, digit in enumerate(isbn):

                weight = 1 if index % 2 == 0 else 3
                total += int(digit) * weight

            return total % 10 == 0

        return False

    # Get book cover URL
    def get_cover_url(self):

        if self.cover_image:
            return f"https://covers.openlibrary.org/b/id/{self.cover_image}-L.jpg"

        if self.isbn:
            return f"https://covers.openlibrary.org/b/isbn/{self.isbn}-L.jpg"

        return None

    # Convert book object to dictionary
    def to_dict(self):

        return {
            "title": self.title,
            "authors": self.authors,
            "isbn": self.isbn,
            "first_publish_year": self.first_publish_year,
            "subjects": self.subjects,
            "page_count": self.page_count,
            "cover_image": self.get_cover_url()
        }
