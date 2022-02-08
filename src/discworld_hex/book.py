import re
from collections import namedtuple
from typing import List

import numpy as np
import spacy
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from wikipedia import WikipediaPage

BookText = namedtuple("BookText", ("book", "text"))


class Book(BaseModel):
    name: str
    content: str = ""
    plot: str = ""
    plot_paragraphs: List[str] = []
    plot_sentences: List[str] = []
    plot_sentences_encoded: List[np.ndarray] = []

    _plot_regex = re.compile(r"(?:== (?:Plot|Synopsis)[^\n]+$)\s*(.+?)\s*^== ", re.MULTILINE | re.S)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_page(cls, page: WikipediaPage):
        return Book(name=page.title, content=page.content)

    def parse_plot(self):
        if match := re.search(self._plot_regex, self.content):
            self.plot = match.group(1)

    def parse_plot_paragraphs(self):
        paragraphs = [x.strip() for x in self.plot.split(sep="\n")]

        self.plot_paragraphs = [x for x in paragraphs if (x and (not x.startswith("==")))]

    def parse_sentences(self, model: spacy.Language):
        sentences = []
        for paragraph in self.plot_paragraphs:
            sentences += [s.text.strip() for s in model(paragraph).sents]
        self.plot_sentences = sentences

    def encode_sentences(self, model: SentenceTransformer):
        self.plot_sentences_encoded = model.encode(self.plot_sentences)
