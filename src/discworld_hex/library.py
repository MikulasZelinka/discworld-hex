import pickle
import re
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np
import spacy
import wikipedia
from loguru import logger
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from discworld_hex.book import Book, BookText
from discworld_hex.sections import SECTIONS

model = SentenceTransformer()


class Library(BaseModel):
    name: str
    books: List[Book] = []

    sentence_splitter_model: spacy.Language = None
    encoder_model: SentenceTransformer = None

    sentence_index: faiss.IndexFlatL2 = None
    sentence_index_to_book_text: Dict[int, BookText] = {}

    _plot_regex = re.compile(r"(?:== (?:Plot|Synopsis)[^\n]+$)\s*(.+?)\s*^== ", re.MULTILINE | re.S)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_book_page_names(
        cls, name: str, book_page_names: List[str], sentence_splitter_model=None, encoder_model=None, limit: int = 0
    ):

        if limit > 0:
            book_page_names = book_page_names[:limit]

        logger.info(f"Library {name} initialising from books with page names: {', '.join(book_page_names)}")

        books = []
        for b in tqdm(book_page_names):
            book = Book.from_page(wikipedia.page(b, auto_suggest=False, redirect=False, preload=False))

            book.parse_plot()
            if not book.plot:
                logger.warning(f"{book.name} has no plot, not adding it.")
                continue

            book.parse_plot_paragraphs()
            book.parse_sentences(sentence_splitter_model)
            book.encode_sentences(encoder_model)
            books.append(book)

        if len(books) <= 0:
            raise ValueError("No books were added")

        logger.success(
            f"{len(books)} books loaded, parsed and encoded successfully: {', '.join(b.name for b in books)}"
        )

        return Library(
            name=name,
            books=books,
            sentence_splitter_model=sentence_splitter_model,
            encoder_model=encoder_model,
        )

    def build_index(self):

        tensors = np.stack([book_sentences for book in self.books for book_sentences in book.plot_sentences_encoded])

        logger.info(f"Building index from {tensors.shape[0]} sentences.")

        tensor_id = 0
        for book in self.books:
            for sentence in book.plot_sentences:
                self.sentence_index_to_book_text[tensor_id] = BookText(book, sentence)
                tensor_id += 1

        index = faiss.IndexFlatL2(tensors.shape[1])
        index.add(tensors)

        assert index.is_trained

        logger.success(
            f"Sentence index built, contains {tensors.shape[0]} sentences with {tensors.shape[1]} elements each."
        )
        self.sentence_index = index

    def save(self, path: Path = None):
        path = path or Path.home()
        path = path / f"{self.name}.pkl"

        logger.info(f"Saving library to {path}")
        with open(path, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        logger.success(f"Saved library to {path}")

    @classmethod
    def load(cls, path: Path):
        logger.info(f"Loading library from {path}")

        with open(path, "rb") as f:
            library = pickle.load(f)

        logger.success(f"Library {library.name} loaded!")
        return library

    def search_interactive(self, k):
        logger.info(
            f"Searching the {self.name} library interactively.\n"
            f"Available books: {len(self.books)} – {', '.join(b.name for b in self.books)}\n"
            f"Looking at {k} nearest neighbours."
        )

        while True:
            sentence = input("Input a sentence: ")

            sentence_encoded = self.encoder_model.encode(sentence)
            distances, indices = self.sentence_index.search(np.stack([sentence_encoded]), k)

            logger.debug(f"distances: {distances}, indices: {indices}")

            # we assume only one sentence query here:
            distances = distances[0]
            indices = indices[0]

            for rank in range(k):
                i = indices[rank]
                book, text = self.sentence_index_to_book_text[i]
                print(f"{(rank + 1):>3}. {text}")
                print(f"   – {book.name}, distance: {distances[rank]:.2f}\n")


def build_library(
    name: str = "Discworld",
    book_page_names: List[str] = SECTIONS["Discworld"],
    sentence_splitter_model_name: str = "en_core_web_sm",
    encoder_model_name: str = "all-mpnet-base-v2",
    limit: int = 0,
    path: Path = None,
):
    logger.info(f"Loading sentence splitter model {sentence_splitter_model_name}")
    sentence_splitter_model = spacy.load(sentence_splitter_model_name)

    logger.info(f"Loading encoder model {encoder_model_name}")
    encoder_model = SentenceTransformer(encoder_model_name)

    library = Library.from_book_page_names(
        name=name,
        book_page_names=book_page_names,
        sentence_splitter_model=sentence_splitter_model,
        encoder_model=encoder_model,
        limit=limit,
    )
    library.build_index()
    library.save(path=path)


def search_library(path: Path = Path.home() / "Discworld.pkl", k: int = 4):
    library = Library.load(path=path)

    library.search_interactive(k)


if __name__ == "__main__":
    build_library()

    search_library()
