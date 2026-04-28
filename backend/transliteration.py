"""Minimal Uzbek Cyrillic/Latin normalization for better search recall.

This is not intended as a perfect transliteration library. It is enough to make
student questions in Uzbek Cyrillic and Uzbek Latin match the same knowledge
base chunks.
"""
from __future__ import annotations

CYR_TO_LAT_PAIRS = [
    ("Ў", "Oʻ"), ("ў", "oʻ"),
    ("Ғ", "Gʻ"), ("ғ", "gʻ"),
    ("Қ", "Q"), ("қ", "q"),
    ("Ҳ", "H"), ("ҳ", "h"),
    ("Ш", "Sh"), ("ш", "sh"),
    ("Ч", "Ch"), ("ч", "ch"),
    ("Ё", "Yo"), ("ё", "yo"),
    ("Ю", "Yu"), ("ю", "yu"),
    ("Я", "Ya"), ("я", "ya"),
    ("Е", "E"), ("е", "e"),
    ("Ц", "Ts"), ("ц", "ts"),
    ("А", "A"), ("а", "a"),
    ("Б", "B"), ("б", "b"),
    ("В", "V"), ("в", "v"),
    ("Г", "G"), ("г", "g"),
    ("Д", "D"), ("д", "d"),
    ("Ж", "J"), ("ж", "j"),
    ("З", "Z"), ("з", "z"),
    ("И", "I"), ("и", "i"),
    ("Й", "Y"), ("й", "y"),
    ("К", "K"), ("к", "k"),
    ("Л", "L"), ("л", "l"),
    ("М", "M"), ("м", "m"),
    ("Н", "N"), ("н", "n"),
    ("О", "O"), ("о", "o"),
    ("П", "P"), ("п", "p"),
    ("Р", "R"), ("р", "r"),
    ("С", "S"), ("с", "s"),
    ("Т", "T"), ("т", "t"),
    ("У", "U"), ("у", "u"),
    ("Ф", "F"), ("ф", "f"),
    ("Х", "X"), ("х", "x"),
    ("Э", "E"), ("э", "e"),
    ("ъ", "ʼ"), ("ь", ""),
]


def to_latin(text: str) -> str:
    result = text
    for cyr, lat in CYR_TO_LAT_PAIRS:
        result = result.replace(cyr, lat)
    return result


def normalize_for_search(text: str) -> str:
    text = text.replace("’", "ʻ").replace("'", "ʻ").replace("`", "ʻ")
    latin = to_latin(text)
    return f"{text}\n{latin}".lower()
