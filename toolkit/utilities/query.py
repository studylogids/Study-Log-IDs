import pathlib
import re

from lxml import etree


ns = {"src": "http://www.srcML.org/srcML/src"}
queryvars = etree.XPath("//src:name/text()", namespaces=ns)
islog = etree.RelaxNG(
    etree.parse(str(pathlib.Path(__file__).parent / "logpattern.rng"))
)


def extractlog(root):
    """find first logging statement"""
    for call in root.iter(r"{*}call"):
        if islog(call):
            yield call


_WORD = re.compile(r"[a-zA-Z][a-z]*")

ID_HEURISTICS = [
    "id",
    "path",
    "address",
    "host",
    "ip",
    "name",
    "url",
    "uri",
]


def isid(variable: str):
    for word in _WORD.findall(variable):
        for heuristic in ID_HEURISTICS:
            if word.lower().endswith(heuristic):
                return True
    return False


def extractid(log):
    for var in queryvars(log):
        if isid(var):
            yield var
