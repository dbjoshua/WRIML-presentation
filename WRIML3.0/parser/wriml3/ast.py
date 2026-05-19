"""
wriml.ast — Nœuds de l'arbre syntaxique abstrait (AST) WRIML v3

Chaque nœud est un dataclass JSON-sérialisable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ────────────────────────────────────────────────────────────────────────────
#  Position dans le source
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class Position:
    line: int
    col: int

    def to_dict(self) -> dict:
        return {"line": self.line, "col": self.col}


# ────────────────────────────────────────────────────────────────────────────
#  Nœuds de base
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class Node:
    """Classe de base pour tous les nœuds AST."""
    pos: Optional[Position] = field(default=None, repr=False)

    def to_dict(self) -> dict:
        raise NotImplementedError

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


@dataclass
class TextNode(Node):
    """Texte nu (hors balises)."""
    text: str = ""

    def to_dict(self) -> dict:
        d: dict = {"type": "text", "text": self.text}
        if self.pos:
            d["pos"] = self.pos.to_dict()
        return d


@dataclass
class ElementNode(Node):
    """
    Élément WRIML : peut être paired, auto-fermant, verbatim, ou quoté.

    Champs :
        name       : nom de la balise (sans '^' ni '_')
        attributes : dict {attr_name: attr_value}
        children   : liste de nœuds enfants (vide pour auto-fermants)
        kind       : 'paired' | 'empty' | 'verbatim' | 'quoted' | 'escape'
        verbatim_content : contenu brut pour les blocs verbatim
        group_separators : positions des ^gs* dans children (indices)
    """
    name: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List[Node] = field(default_factory=list)
    kind: str = "paired"
    verbatim_content: Optional[str] = None
    group_separators: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        d: dict = {
            "type": "element",
            "name": self.name,
            "kind": self.kind,
            "attributes": self.attributes,
        }
        if self.pos:
            d["pos"] = self.pos.to_dict()
        if self.kind == "verbatim" and self.verbatim_content is not None:
            d["verbatim_content"] = self.verbatim_content
        else:
            d["children"] = [c.to_dict() for c in self.children]
        if self.group_separators:
            d["group_separators"] = self.group_separators
        return d


@dataclass
class ControlNode(Node):
    """Nœud de contrôle : happy-ending (^_*), EOT (^eot*), GS (^gs*)."""
    control: str = ""   # "happy_ending" | "eot" | "gs"

    def to_dict(self) -> dict:
        d: dict = {"type": "control", "control": self.control}
        if self.pos:
            d["pos"] = self.pos.to_dict()
        return d


@dataclass
class DocumentNode(Node):
    """Racine du document — peut être multi-racine."""
    children: List[Node] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "type": "document",
            "children": [c.to_dict() for c in self.children],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
