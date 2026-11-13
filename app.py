import streamlit as st
import json
import os
import csv
import io

from open_library import OpenLibraryClient
from book import Book
from reading_list import ReadingListManager
from ai_generator import ReadingGuideGenerator


# Page configuration
st.set_page_config(
    page_title="AI Book Reading Assistant",
    page_icon="📚",
    layout="wide"
)


# Create application objects
client = OpenLibraryClient()
reading_manager = ReadingListManager()
guide_generator = ReadingGuideGenerator()


# Initialize session state
if "results" not in st.session_state:
    st.session_state.results = []

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# Application title
st.title("📚 AI Book Reading Assistant")

st.write(
    "Discover books, generate AI reading guides, "
    "track your reading progress and explore recommendations."
)

st.divider()


# Sidebar navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a section",
    ["Home", "Search Books", "My Favourites"]
)


# HOME PAGE
if page == "Home":

    st.header("Welcome to Your Reading Assistant!")

    st.write(
        "Your personal reading companion powered by "
        "Open Library and Google Gemini AI."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📖 Search for books")

    with col2:
        st.info("🤖 Generate AI reading guides")

    with col3:
        st.info("⭐ Save favourite books")

    st.subheader("What can you do?")

    st.write("""
    - Search for books by title, author or ISBN.
    - View book information and cover images.
    - Generate AI summaries and comprehension questions.
    - Track your reading progress.
    - Discover similar books.
    - Save and export your favourite books.
    """)


# SEARCH BOOKS PAGE
elif page == "Search Books":

    st.header("🔍 Search for Books")

    search_method = st.selectbox(
        "Choose your search method",
        ["Title", "Author", "ISBN"]
    )

    search_input = st.text_input("Enter your search")

    if st.button("Search Books"):

        if search_input.strip():

            try:

                if search_method == "Title":
                    results = client.search_by_title(search_input)

                elif search_method == "Author":
                    results = client.search_by_author(search_input)

                else:
                    results = client.search_by_isbn(search_input)

                st.session_state.results = results
                st.session_state.selected_book = None

            except Exception as e:
                st.error(f"Search failed: {e}")

        else:
            st.warning("Please enter a search term.")

    results = st.session_state.results

    if results:

        st.success(f"{len(results)} books found!")

        book_options = [
            f"{index + 1}. {result.get('title', 'Unknown title')}"
            for index, result in enumerate(results)
        ]

        selected_option = st.selectbox(
            "Select a book",
            book_options
        )

        selected_index = book_options.index(selected_option)

        first_book = results[selected_index]

        book = Book(
            title=first_book.get("title"),
            authors=first_book.get("author_name", []),
            isbn=(first_book.get("isbn") or [None])[0],
            first_publish_year=first_book.get("first_publish_year"),
            subjects=first_book.get("subject"),
            page_count=first_book.get("number_of_pages_median"),
            cover_image=first_book.get("https://covers.openlibrary.org/b/id/{self.cover_image}-L.jpg")
        )

        st.divider()

        st.subheader("📖 Book Information")

        col1, col2 = st.columns([1, 2])

        with col1:

            cover_url = book.get_cover_url()

            if cover_url:
                st.image(cover_url, width=220)

        with col2:

            st.write(f"**Title:** {book.title}")

            st.write(
                f"**Author(s):** {', '.join(book.authors) if book.authors else 'Unknown'}"
            )

            st.write(f"**ISBN:** {book.isbn or 'Not available'}")

            st.write(
                f"**Publication Year:** {book.first_publish_year or 'Not available'}"
            )

            st.write(f"**Page Count:** {book.page_count or 'Not available'}")

            st.write(
                f"**ISBN Status:** {'Valid' if book.validate_isbn() else 'Invalid or unavailable'}"
            )

        st.divider()

        # AI READING GUIDE
        st.subheader("🤖 AI Reading Guide")

        if st.button("Generate Reading Guide"):

            try:

                with st.spinner("Generating your reading guide..."):

                    guide = guide_generator.generate_reading_guide(book)

                st.session_state["current_guide"] = guide
                st.session_state["guide_book"] = book.title

            except Exception as e:
                st.error(f"Unable to generate guide: {e}")

        if (
            "current_guide" in st.session_state
            and st.session_state.get("guide_book") == book.title
        ):

            st.markdown(st.session_state.current_guide)

            if st.button("Save Reading Guide"):

                guide_data = {
                    "title": book.title,
                    "authors": book.authors,
                    "publication_year": book.first_publish_year,
                    "reading_guide": st.session_state.current_guide
                }

                try:

                    if os.path.exists("reading_guides.json"):

                        with open("reading_guides.json", "r") as file:
                            guides = json.load(file)

                    else:
                        guides = []

                    guides.append(guide_data)

                    with open("reading_guides.json", "w") as file:
                        json.dump(guides, file, indent=4)

                    st.success("Reading guide saved successfully!")

                except (OSError, json.JSONDecodeError) as e:
                    st.error(f"Unable to save reading guide: {e}")

        st.divider()

        # READING STATUS
        st.subheader("📌 Reading Progress")

        reading_status = st.selectbox(
            "Choose your reading status",
            ["Want to Read", "Currently Reading", "Finished"]
        )

        if st.button("Save to Favourites"):

            book_data = book.to_dict()
            book_data["reading_status"] = reading_status

            reading_manager.add_book(book_data)

            st.success("Book saved to your favourites!")

        st.divider()

        # RECOMMENDATIONS
        st.subheader("📚 Similar Books")

        if book.subjects:

            try:

                subject = book.subjects[0]

                recommendations = client.search_by_subject(subject)

                for recommendation in recommendations:

                    st.write(
                        f"**{recommendation.get('title')}**"
                    )

                    authors = recommendation.get("author_name", [])

                    st.caption(
                        f"Author: {', '.join(authors) if authors else 'Unknown'}"
                    )

            except Exception as e:
                st.error(f"Unable to retrieve recommendations: {e}")

        else:
            st.info("No subjects available for recommendations.")


# MY FAVOURITES PAGE
elif page == "My Favourites":

    st.header("⭐ My Favourite Books")

    try:

        favourites = reading_manager.load_books()

        if favourites:

            for index, book in enumerate(favourites, start=1):

                with st.expander(f"{index}. {book['title']}"):

                    st.write(
                        f"**Author(s):** {', '.join(book['authors'])}"
                    )

                    st.write(
                        f"**Publication Year:** {book['first_publish_year']}"
                    )

                    st.write(
                        f"**Reading Status:** {book.get('reading_status', 'Not set')}"
                    )

                    if book.get("cover_image"):
                        st.image(book["cover_image"], width=120)

            # CSV EXPORT
            output = io.StringIO()

            if favourites:

                writer = csv.DictWriter(
                    output,
                    fieldnames=favourites[0].keys()
                )

                writer.writeheader()
                writer.writerows(favourites)

                st.download_button(
                    label="📥 Download Reading List as CSV",
                    data=output.getvalue(),
                    file_name="reading_list.csv",
                    mime="text/csv"
                )

        else:
            st.info("You haven't saved any favourite books yet.")

    except (OSError, json.JSONDecodeError) as e:
        st.error(f"Unable to load favourites: {e}")
