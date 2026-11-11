import requests


class OpenLibraryClient:

    SEARCH_URL = "https://openlibrary.org/search.json"

    # Search by title
    def search_by_title(self, title):

        params = {
            "title": title,
            "fields": "title,author_name,isbn,first_publish_year,subject,number_of_pages_median,cover_i",
            "limit": 10
        }

        response = requests.get(self.SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("docs", [])

    # Search by author
    def search_by_author(self, author):

        params = {
            "author": author,
            "fields": "title,author_name,isbn,first_publish_year,subject,number_of_pages_median,cover_i",
            "limit": 10
        }

        response = requests.get(self.SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("docs", [])

    # Search by ISBN
    def search_by_isbn(self, isbn):

        params = {
            "isbn": isbn,
            "fields": "title,author_name,isbn,first_publish_year,subject,number_of_pages_median,cover_i",
            "limit": 10
        }

        response = requests.get(self.SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("docs", [])

    # Search for similar books by subject
    def search_by_subject(self, subject):

        params = {
            "subject": subject,
            "fields": "title,author_name,first_publish_year",
            "limit": 5
        }

        response = requests.get(self.SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("docs", [])
