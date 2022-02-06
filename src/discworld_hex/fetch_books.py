import wikipedia
from loguru import logger
from tqdm import tqdm

from discworld_hex.book import Book

# Source: https://en.wikipedia.org/wiki/Category:Discworld_books
BOOKS = [
    "The Amazing Maurice and His Educated Rodents",
    "The Art of Discworld",
    "A Blink of the Screen",
    "Carpe Jugulum",
    "The Colour of Magic",
    "Death's Domain",
    "The Discworld Almanak",
    "The Discworld Companion",
    "Discworld Diary",
    "Equal Rites",
    "Eric (novel)",
    "Feet of Clay (novel)",
    "The Fifth Elephant",
    "Going Postal",
    "Guards! Guards!",
    "A Hat Full of Sky",
    "Hogfather",
    "I Shall Wear Midnight",
    "Interesting Times",
    "Jingo (novel)",
    "The Last Continent",
    "The Last Hero",
    "The Light Fantastic",
    "Lords and Ladies (novel)",
    "Making Money",
    "The Discworld Mapp",
    "Maskerade",
    "Men at Arms",
    "Monstrous Regiment (novel)",
    "Mort",
    "Moving Pictures (novel)",
    "Nanny Ogg's Cookbook",
    "Night Watch (Discworld)",
    "Once More* with Footnotes",
    "The Pratchett Portfolio",
    "Pyramids (novel)",
    "Raising Steam",
    "Reaper Man",
    "The Science of Discworld",
    "The Science of Discworld II: The Globe",
    "The Science of Discworld III: Darwin's Watch",
    "The Science of Discworld IV: Judgement Day",
    "The Shepherd's Crown",
    "Small Gods",
    "Snuff (Pratchett novel)",
    "Soul Music (novel)",
    "Sourcery",
    "The Streets of Ankh-Morpork",
    "Thief of Time",
    "Thud!",
    "A Tourist Guide to Lancre",
    "The Truth (novel)",
    "Unseen Academicals",
    "The Unseen University Challenge",
    "The Unseen University Cut Out Book",
    "The Wee Free Men",
    "Where's My Cow?",
    "Wintersmith",
    "The Wit and Wisdom of Discworld",
    "Witches Abroad",
    "The World of Poo",
    "Wyrd Sisters",
]


def find_books():
    # Too unreliable:
    # return wikipedia.search("discworld novel", results=500)
    return BOOKS


def fetch_books(book_page_names):
    books = []
    for b in tqdm(book_page_names):
        book = Book.from_page(wikipedia.page(b, auto_suggest=False, redirect=False, preload=False))
        book.parse_plot()
        if book.plot:
            book.parse_plot_paragraphs()
            books.append(book)
        else:
            logger.warning(f"Book {book.name} has no plot, not adding it.")
    return books


if __name__ == "__main__":
    book_page_names = find_books()
    books = fetch_books(book_page_names)
