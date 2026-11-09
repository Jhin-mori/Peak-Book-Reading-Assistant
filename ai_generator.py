from google import genai
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()

# Connect to Gemini
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class ReadingGuideGenerator:

    def generate_reading_guide(self, book):

        prompt = f"""
        Create a reading guide for the following book:

        Title: {book.title}
        Author: {', '.join(book.authors)}
        Publication Year: {book.first_publish_year}

        Include:

        1. A clear summary of the book.
        2. The reading difficulty level
           (Beginner, Intermediate or Advanced).
        3. Five comprehension questions.

        Organize your response with clear headings.
        """

        response = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        return response.output_text