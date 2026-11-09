import re


# Clean ISBN numbers using regular expressions
def clean_isbn(isbn):

    if not isbn:
        return None

    return re.sub(r"[^0-9Xx]", "", str(isbn)).upper()


