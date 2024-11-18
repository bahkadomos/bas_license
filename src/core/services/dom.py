from collections.abc import Sequence
from lxml import etree


class HTMLParser:
    def __init__(self):
        self._parser = etree.HTMLParser()

    def get_by_xpath(self, html: str, query: str) -> str | None:
        dom = etree.fromstring(html, self._parser)
        data = dom.xpath(query)
        if isinstance(data, Sequence) and isinstance(data[0], str):
            return data[0]
