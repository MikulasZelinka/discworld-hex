import re
from typing import List

from pydantic import BaseModel
from wikipedia import WikipediaPage


class Book(BaseModel):
    name: str
    content: str = ""
    plot: str = ""
    plot_paragraphs: List[str] = []

    _plot_regex = re.compile(r"(?:== (?:Plot|Synopsis)[^\n]+$)\s*(.+?)\s*^== ", re.MULTILINE | re.S)

    @classmethod
    def from_page(cls, page: WikipediaPage):
        return Book(name=page.title, content=page.content)

    def parse_plot(self):
        if match := re.search(self._plot_regex, self.content):
            self.plot = match.group(1)

    def parse_plot_paragraphs(self):
        paragraphs = [x.strip() for x in self.plot.split(sep="\n")]

        self.plot_paragraphs = [x for x in paragraphs if (x and (not x.startswith("==")))]
