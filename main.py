import json
import os

from reading_list import ReadingListManager
from open_library import OpenLibraryClient
from book import Book
from ai_generator import ReadingGuideGenerator


# View saved favourite books
def view_favourites():

    if os.path.exists("favourites.json"):

        with open("favourites.json", "r") as file:
            favourites = json.load(file)

        if favourites:
            print("\n====== YOUR FAVOURITE BOOKS ======")

            for index, book in enumerate(favourites, start=1):

                print(f"\n{index}. {book['title']}")
                print(f"Author(s): {', '.join(book['authors'])}")
                print(f"Publication Year: {book['first_publish_year']}")
                print(f"Reading Status: {book.get('reading_status', 'Not set')}")

            print("\n==================================")

        else:
            print("You haven't saved any favourite books yet.")

    else:
        print("You haven't saved any favourite books yet.")


# Create objects
client = OpenLibraryClient()
guide_generator = ReadingGuideGenerator()
reading_manager = ReadingListManager()


# Choose search method
print("\n====== BOOK SEARCH ======")
print("1. Search by Title")
print("2. Search by Author")
print("3. Search by ISBN")

search_choice = input("\nChoose your search method (1-3): ")

if search_choice == "1":

    title = input("Enter the book title: ")
    results = client.search_by_title(title)

elif search_choice == "2":

    author = input("Enter the author's name: ")
    results = client.search_by_author(author)

elif search_choice == "3":

    isbn = input("Enter the book ISBN: ")
    results = client.search_by_isbn(isbn)

else:

    print("Invalid search choice.")
    results = []


# Check search results
if results:

    # Display search results
    for index, result in enumerate(results, start=1):

        print(f"\n{index}. {result.get('title')}")

        authors = result.get("author_name", [])
        print(f"Author: {', '.join(authors) if authors else 'Unknown'}")

        print(f"Publication Year: {result.get('first_publish_year', 'Unknown')}")

    # Allow the user to select a book
    while True:
        try:
            choice = int(input("\nSelect a book number: "))

            if 1 <= choice <= len(results):

                first_book = results[choice - 1]

                # Create a Book object
                book = Book(
                    title=first_book.get("title"),
                    authors=first_book.get("author_name", []),
                    isbn=(first_book.get("isbn") or [None])[0],
                    first_publish_year=first_book.get("first_publish_year"),
                    subjects=first_book.get("subject"),
                    page_count=first_book.get("number_of_pages_median"),
                    cover_image=first_book.get("cover_i")
                )

                # Display selected book information
                book.display_info()

                # Generate AI Reading Guide
                guide_choice = input(
                    "\nWould you like an AI reading guide for this book? (yes/no): "
                )

                if guide_choice.lower() == "yes":

                    print("\nGenerating your reading guide... Please chill")

                    try:
                        guide = guide_generator.generate_reading_guide(book)

                        print("\n------ AI READING GUIDE ------")
                        print(guide)
                        print("----------------------------------")

                        # Save AI reading guide
                        guide_data = {
                            "title": book.title,
                            "authors": book.authors,
                            "publication_year": book.first_publish_year,
                            "reading_guide": guide
                        }

                        if os.path.exists("reading_guides.json"):
                            with open("reading_guides.json", "r") as file:
                                guides = json.load(file)
                        else:
                            guides = []

                        guides.append(guide_data)

                        with open("reading_guides.json", "w") as file:
                            json.dump(guides, file, indent=4)

                        print("\nReading guide saved successfully!")

                    except Exception as e:
                        print("Unable to generate your reading guide:", e)

                # Validate ISBN
                if book.validate_isbn():
                    print("ISBN status: Valid")
                else:
                    print("ISBN status: Invalid or unavailable")

                # Display book cover URL
                print("Cover URL:", book.get_cover_url())

                # Choose reading status
                while True:

                    print("\nChoose your reading status:")
                    print("1. Want to Read")
                    print("2. Currently Reading")
                    print("3. Finished")

                    status_choice = input("Enter your choice (1-3): ")

                    if status_choice == "1":
                        reading_status = "Want to Read"
                        break

                    elif status_choice == "2":
                        reading_status = "Currently Reading"
                        break

                    elif status_choice == "3":
                        reading_status = "Finished"
                        break

                    else:
                        print("Invalid choice. Please select 1, 2 or 3.")

                # Convert book object to dictionary
                book_data = book.to_dict()
                book_data["reading_status"] = reading_status

                print(book_data)

                # Save book to favourites
                save_choice = input(
                    "\nWould you like to save this book to favourites? (yes/no): "
                )

                if save_choice.lower() == "yes":

                    reading_manager.add_book(book_data)

                    print("Book saved to favourites successfully!")

                else:
                    print("Book was not saved.")

                # Book recommendations
                print("\n------ BOOK RECOMMENDATIONS ------")

                if book.subjects:

                    subject = book.subjects[0]

                    recommendations = client.search_by_subject(subject)

                    for index, recommendation in enumerate(recommendations, start=1):

                        print(f"{index}. {recommendation.get('title')}")

                        authors = recommendation.get("author_name", [])
                        print(
                            f"   Author: {', '.join(authors) if authors else 'Unknown'}"
                        )

                else:
                    print("No subjects available for recommendations.")

                # View favourites
                view_choice = input(
                    "\nWould you like to view your favourite books? (yes/no): "
                )

                if view_choice.lower() == "yes":
                    view_favourites()

                # Export reading list to CSV
                export_choice = input(
                    "\nWould you like to export your reading list to CSV? (yes/no): "
                )

                if export_choice.lower() == "yes":
                    reading_manager.export_to_csv()

                break

            else:
                print("Invalid selection. Please choose a number from the list.")

        except ValueError:
            print("Please enter a valid number.")

else:
    print("No book found.")