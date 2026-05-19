"""
wriml — API publique du parseur minimal WRIML v3

Usage minimal :

    from wriml import parse

    doc = parse("^section:Bonjour_section:")
    print(doc.children)
    print(doc.to_json())

Ou depuis un fichier :

    from wriml import parse_file

    doc = parse_file("document.wriml")
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from .ast import DocumentNode
from .errors import LexerError, ParseError, WRIMLError
from .lexer import Lexer
from .parser import Parser

__all__ = [
    "parse",
    "parse_file",
    "WRIMLError",
    "LexerError",
    "ParseError",
    "DocumentNode",
]

__version__ = "0.1.0"


def parse(source: str) -> DocumentNode:
    """
    Parse une chaîne WRIML et retourne un DocumentNode (AST).

    :param source: Contenu WRIML en texte (str).
    :returns: DocumentNode racine de l'AST.
    :raises LexerError: Erreur de tokenisation.
    :raises ParseError: Erreur syntaxique.
    """
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def parse_file(path: Union[str, Path]) -> DocumentNode:
    """
    Ouvre un fichier .wriml (UTF-8) et retourne son AST.

    :param path: Chemin vers le fichier WRIML.
    :returns: DocumentNode racine de l'AST.
    :raises FileNotFoundError: Si le fichier est introuvable.
    :raises LexerError: Erreur de tokenisation.
    :raises ParseError: Erreur syntaxique.
    """
    content = Path(path).read_text(encoding="utf-8")
    return parse(content)
