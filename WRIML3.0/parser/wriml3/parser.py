"""
wriml.parser — Parser WRIML v3

Produit un DocumentNode (AST) à partir d'une liste de tokens issue du lexer.

Architecture :
    parse_document()
      └─ parse_node()           (dispatch principal)
            ├─ parse_element()  (OPEN_TAG → contenu → CLOSE_TAG)
            ├─ parse_empty()    (EMPTY_TAG)
            ├─ parse_control()  (HAPPY_ENDING / EOT / GS)
            └─ parse_text()     (TEXT)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .ast import (
    ControlNode,
    DocumentNode,
    ElementNode,
    Node,
    Position,
    TextNode,
)
from .errors import ParseError
from .tokens import Token, TokenType

# Noms de balises verbatim reconnus par le parser
_VERBATIM_NAMES = {"code", "com", "cmt", "rem", "comment", "-", "#"}

# Alias de paragraphes
_PARAGRAPH_NAMES = {"p", "par", "paragraph"}


class Parser:
    """
    Consomme une liste de tokens et construit un AST.

    Usage :
        ast = Parser(tokens).parse()
    """

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # ------------------------------------------------------------------ #
    #  Point d'entrée                                                      #
    # ------------------------------------------------------------------ #

    def parse(self) -> DocumentNode:
        doc = DocumentNode()
        while not self._at(TokenType.EOF):
            node = self._parse_node(context_tag=None)
            if node is not None:
                doc.children.append(node)
        return doc

    # ------------------------------------------------------------------ #
    #  Dispatch                                                            #
    # ------------------------------------------------------------------ #

    def _parse_node(self, context_tag: Optional[str]) -> Optional[Node]:
        """
        Produit le prochain nœud.
        Retourne None quand la portée courante est terminée
        (CLOSE_TAG correspondant, HAPPY_ENDING, EOT à la racine).
        """
        tok = self._peek()

        if tok.type == TokenType.EOF:
            return None

        if tok.type == TokenType.TEXT:
            return self._parse_text()

        if tok.type == TokenType.VERBATIM:
            return self._parse_text()  # verbatim brut déjà dans le texte

        if tok.type == TokenType.OPEN_TAG:
            return self._parse_element()

        if tok.type == TokenType.EMPTY_TAG:
            return self._parse_empty()

        if tok.type == TokenType.HAPPY_ENDING:
            # Ferme la portée courante (ou le document si à la racine)
            self._advance()
            return None  # signal de fin de portée

        if tok.type == TokenType.EOT:
            if context_tag is not None:
                raise ParseError(
                    "'^eot*' est interdit à l'intérieur d'un élément.",
                    tok.line, tok.col,
                    hint=f"Balise ouverte en attente de fermeture : '_{context_tag}:'",
                )
            # Avance jusqu'à EOF — tout ce qui suit ^eot* est ignoré
            while not self._at(TokenType.EOF):
                self._advance()
            return None  # termine le document

        if tok.type == TokenType.GS:
            if context_tag is None:
                raise ParseError(
                    "'^gs*' (Group Separator) est interdit à la racine du document.",
                    tok.line, tok.col,
                )
            self._advance()
            return ControlNode(control="gs", pos=Position(tok.line, tok.col))

        if tok.type == TokenType.CLOSE_TAG:
            # On laisse le caller traiter la fermeture
            return None

        raise ParseError(
            f"Token inattendu : {tok.type.name} ({tok.value!r})",
            tok.line, tok.col,
        )

    # ------------------------------------------------------------------ #
    #  Texte                                                               #
    # ------------------------------------------------------------------ #

    def _parse_text(self) -> TextNode:
        tok = self._advance()
        return TextNode(text=tok.value, pos=Position(tok.line, tok.col))

    # ------------------------------------------------------------------ #
    #  Élément auto-fermant                                               #
    # ------------------------------------------------------------------ #

    def _parse_empty(self) -> ElementNode:
        tok = self._advance()  # EMPTY_TAG
        attrs = self._collect_attributes()
        return ElementNode(
            name=tok.value,
            attributes=attrs,
            kind="escape" if tok.value in {"cfx", "us", "underscore", "dash", "chr", "char"}
                 else "empty",
            pos=Position(tok.line, tok.col),
        )

    # ------------------------------------------------------------------ #
    #  Élément paired (ou verbatim, ou quoté)                            #
    # ------------------------------------------------------------------ #

    def _parse_element(self) -> ElementNode:
        open_tok = self._advance()  # OPEN_TAG
        name = open_tok.value
        pos = Position(open_tok.line, open_tok.col)

        # Récupère les attributs qui suivent immédiatement l'OPEN_TAG
        attrs, is_verbatim, is_quoted = self._collect_element_attributes()

        # --- Bloc verbatim ---
        if is_verbatim:
            verbatim_tok = self._advance()  # VERBATIM
            close_tok = self._advance()     # CLOSE_TAG implicite
            if close_tok.type != TokenType.CLOSE_TAG or close_tok.value != name:
                raise ParseError(
                    f"Bloc verbatim '^{name}:' non fermé correctement.",
                    open_tok.line, open_tok.col,
                )
            return ElementNode(
                name=name,
                attributes=attrs,
                kind="verbatim",
                verbatim_content=verbatim_tok.value,
                pos=pos,
            )

        # --- Forme quotée ---
        if is_quoted:
            # Le texte inline a déjà été tokenisé comme TEXT suivi de QUOTE_MARK
            inline_text = ""
            if self._at(TokenType.TEXT):
                inline_text = self._advance().value
            if self._at(TokenType.QUOTE_MARK):
                self._advance()  # consomme ''
            return ElementNode(
                name=name,
                attributes=attrs,
                kind="quoted",
                children=[TextNode(text=inline_text, pos=pos)],
                pos=pos,
            )

        # --- Élément paired normal ---
        children: List[Node] = []
        gs_positions: List[int] = []

        while True:
            if self._at(TokenType.EOF):
                raise ParseError(
                    f"Balise '^{name}:' non fermée : fin de fichier atteinte.",
                    open_tok.line, open_tok.col,
                    hint=f"Ajoutez '_{name}:' pour fermer l'élément.",
                )

            # Fermeture happy-ending
            if self._at(TokenType.HAPPY_ENDING):
                self._advance()
                break  # ferme cette portée

            # Fermeture normale
            if self._at(TokenType.CLOSE_TAG):
                close_tok = self._peek()
                if close_tok.value == name:
                    self._advance()
                    break
                else:
                    raise ParseError(
                        f"Balise fermante '_{close_tok.value}:' inattendue.",
                        close_tok.line, close_tok.col,
                        hint=f"Balise ouverte attendue : '_{name}:'",
                    )

            # Group Separator
            if self._at(TokenType.GS):
                gs_tok = self._advance()
                gs_positions.append(len(children))
                # On n'ajoute pas de nœud GS dans les enfants — on note la position
                continue

            node = self._parse_node(context_tag=name)
            if node is None:
                # Portée fermée par happy-ending ou EOT (EOT lèverait une erreur au-dessus)
                break
            children.append(node)

        return ElementNode(
            name=name,
            attributes=attrs,
            children=children,
            kind="paired",
            group_separators=gs_positions if gs_positions else [],
            pos=pos,
        )

    # ------------------------------------------------------------------ #
    #  Collecte des attributs après un OPEN_TAG                           #
    # ------------------------------------------------------------------ #

    def _collect_element_attributes(
        self,
    ) -> Tuple[Dict[str, str], bool, bool]:
        """
        Lit les tokens ATTR_NAME / ATTR_VALUE qui suivent un OPEN_TAG.

        Retourne (attrs_dict, is_verbatim, is_quoted).
        is_verbatim : True si __verbatim__ est présent.
        is_quoted   : True si __quoted__ est présent.
        """
        attrs: Dict[str, str] = {}
        is_verbatim = False
        is_quoted = False

        while self._at(TokenType.ATTR_NAME):
            name_tok = self._advance()
            aname = name_tok.value

            if aname == "__verbatim__":
                is_verbatim = True
                continue
            if aname == "__quoted__":
                is_quoted = True
                continue

            if self._at(TokenType.ATTR_VALUE):
                attrs[aname] = self._advance().value
            else:
                raise ParseError(
                    f"Attribut '{aname}' : valeur manquante.",
                    name_tok.line, name_tok.col,
                )

        return attrs, is_verbatim, is_quoted

    def _collect_attributes(self) -> Dict[str, str]:
        """Variante sans flags spéciaux (pour les empty-elements)."""
        attrs, _, _ = self._collect_element_attributes()
        return attrs

    # ------------------------------------------------------------------ #
    #  Helpers de curseur                                                  #
    # ------------------------------------------------------------------ #

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        if tok.type != TokenType.EOF:
            self._pos += 1
        return tok

    def _at(self, ttype: TokenType) -> bool:
        return self._tokens[self._pos].type == ttype
