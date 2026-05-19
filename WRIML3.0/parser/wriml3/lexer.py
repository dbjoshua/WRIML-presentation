"""
wriml.lexer — Lexer WRIML v3

Flux de tokenisation. Le lexer produit une liste plate de tokens que le
parser consomme séquentiellement.

Règles importantes issues de la grammaire officielle :
  - '^' est TOUJOURS actif.
  - "''" est un digraphe atomique (délimiteur de valeur d'attribut et
    de la forme quotée).
  - '_' seul, non suivi d'un element-name + ':', est du texte libre.
  - Les blocs verbatim (^code:, ^com:, ^cmt:, ^rem:, ^-:, ^#:, ^comment:)
    sont capturés en entier sans aucune interprétation interne.
"""

from __future__ import annotations

from typing import List

from .tokens import Token, TokenType
from .errors import LexerError

# Noms qui introduisent un bloc verbatim (fermeture : _<même nom>:)
_VERBATIM_NAMES = {"code", "com", "cmt", "rem", "comment", "-", "#"}

# Noms réservés de contrôle (auto-fermants spéciaux)
_CONTROL_STARS = {"_": TokenType.HAPPY_ENDING, "eot": TokenType.EOT, "gs": TokenType.GS}

# Caractères valides dans un nom de balise (après la première lettre)
_SAFE_L2 = set("@$£~`+&#|")


def _is_letter(ch: str) -> bool:
    return ch.isascii() and ch.isalpha()


def _is_digit(ch: str) -> bool:
    return ch.isascii() and ch.isdigit()


def _is_name_start(ch: str) -> bool:
    """Un nom peut aussi commencer par '_', '-', '#' (reserved-names)."""
    return _is_letter(ch) or ch in ("-", "_", "#")


def _is_name_char(ch: str) -> bool:
    return _is_letter(ch) or _is_digit(ch) or ch in ("-", "_") or ch in _SAFE_L2 or ch == "."


class Lexer:
    """
    Convertit une chaîne source WRIML en liste de tokens.

    Usage :
        tokens = Lexer(source).tokenize()
    """

    def __init__(self, source: str) -> None:
        # Normalise les fins de ligne : CRLF / CR → LF
        self._src = source.replace("\r\n", "\n").replace("\r", "\n")
        self._pos = 0
        self._line = 1
        self._col = 1
        self._tokens: List[Token] = []

    # ------------------------------------------------------------------ #
    #  Point d'entrée                                                      #
    # ------------------------------------------------------------------ #

    def tokenize(self) -> List[Token]:
        while not self._eof():
            if self._peek() == "^":
                self._read_active()
            elif self._peek() == "_":
                # Peut être une balise fermante ou du texte libre
                self._read_possible_close_tag()
            else:
                self._read_text()
        self._emit(TokenType.EOF, "", self._line, self._col)
        return self._tokens

    # ------------------------------------------------------------------ #
    #  Lecture d'un élément actif commençant par '^'                      #
    # ------------------------------------------------------------------ #

    def _read_active(self) -> None:
        start_line, start_col = self._line, self._col
        self._advance()  # consomme '^'

        if self._eof():
            raise LexerError("'^' en fin de fichier", start_line, start_col)

        # Peek du nom
        name = self._read_name()
        if not name:
            raise LexerError(
                f"Caractère inattendu après '^' : {self._peek()!r}",
                start_line, start_col,
            )

        # --- Contrôles spéciaux (^_*, ^eot*, ^gs*) ---
        if name in _CONTROL_STARS:
            # Doit être suivi de '*'
            if self._peek() == "*":
                self._advance()
                self._emit(_CONTROL_STARS[name], f"^{name}*", start_line, start_col)
            else:
                raise LexerError(
                    f"'^{name}' doit être suivi de '*'", start_line, start_col
                )
            return

        # --- Blocs verbatim (^code:, ^com:, …) ---
        if name in _VERBATIM_NAMES:
            self._read_verbatim_block(name, start_line, start_col)
            return

        # --- Éléments d'échappement auto-fermants (^cfx*, ^us*, ^dash*, …) ---
        escape_stars = {"cfx", "us", "underscore", "dash", "chr", "char"}
        if name in escape_stars:
            # Peut avoir des attributs puis '*'
            attrs = self._read_attribute_list()
            if self._peek() != "*":
                raise LexerError(
                    f"'^{name}' : '*' attendu après les attributs", start_line, start_col
                )
            self._advance()
            # On émet comme EMPTY_TAG — l'AST fera la distinction
            self._emit(TokenType.EMPTY_TAG, name, start_line, start_col)
            for tok in attrs:
                self._tokens.append(tok)
            return

        # --- Élément ordinaire ---
        # Lit les attributs éventuels
        attrs = self._read_attribute_list()

        if self._eof():
            raise LexerError(
                f"Fin de fichier inattendue après '^{name}'", start_line, start_col
            )

        ch = self._peek()

        if ch == ":":
            # Balise ouvrante paired : ^name ...:
            self._advance()
            self._emit(TokenType.OPEN_TAG, name, start_line, start_col)
            for tok in attrs:
                self._tokens.append(tok)

        elif ch == "*":
            # Élément auto-fermant : ^name ...*
            self._advance()
            self._emit(TokenType.EMPTY_TAG, name, start_line, start_col)
            for tok in attrs:
                self._tokens.append(tok)

        elif self._src[self._pos:self._pos + 2] == "''":
            # Forme quotée : ^name''contenu''
            self._advance(); self._advance()  # consomme ''
            self._emit(TokenType.OPEN_TAG, name, start_line, start_col)
            for tok in attrs:
                self._tokens.append(tok)
            # Attribut fictif pour signaler la forme quotée
            self._emit(TokenType.ATTR_NAME, "__quoted__", start_line, start_col)
            # Lit le contenu jusqu'au prochain ''
            content_line, content_col = self._line, self._col
            content = self._read_until_quote_mark()
            self._emit(TokenType.TEXT, content, content_line, content_col)
            # close ''
            self._emit(TokenType.QUOTE_MARK, "''", self._line, self._col)
        else:
            raise LexerError(
                f"'^{name}' : ':' ou '*' ou \"''\" attendu, trouvé {ch!r}",
                start_line, start_col,
            )

    # ------------------------------------------------------------------ #
    #  Lecture d'une fermeture potentielle _name:                         #
    # ------------------------------------------------------------------ #

    def _read_possible_close_tag(self) -> None:
        """'_' peut introduire une balise fermante ou être du texte."""
        save_pos = self._pos
        save_line, save_col = self._line, self._col

        self._advance()  # consomme '_'
        name = self._read_name()
        if name and not self._eof() and self._peek() == ":":
            self._advance()  # consomme ':'
            self._emit(TokenType.CLOSE_TAG, name, save_line, save_col)
        else:
            # Ce n'est pas une balise fermante — revient en arrière
            self._pos = save_pos
            self._line = save_line
            self._col = save_col
            self._read_text()

    # ------------------------------------------------------------------ #
    #  Lecture d'un bloc verbatim                                         #
    # ------------------------------------------------------------------ #

    def _read_verbatim_block(self, name: str, sl: int, sc: int) -> None:
        """Lit ^name[attrs]: ... _name: en capturant tout le contenu brut."""
        attrs = self._read_attribute_list()
        if self._eof() or self._peek() != ":":
            raise LexerError(
                f"'^{name}' : ':' attendu pour ouvrir le bloc verbatim", sl, sc
            )
        self._advance()  # consomme ':'

        close_marker = f"_{name}:"
        content_parts: List[str] = []
        content_line, content_col = self._line, self._col

        while not self._eof():
            remaining = self._src[self._pos:]
            idx = remaining.find(close_marker)
            if idx == -1:
                raise LexerError(
                    f"Bloc verbatim '^{name}:' non fermé (manque '{close_marker}')", sl, sc
                )
            content_parts.append(remaining[:idx])
            # Avance le curseur de idx + len(close_marker)
            for ch in remaining[:idx]:
                self._advance_char(ch)
            for _ in close_marker:
                self._advance()
            break

        self._emit(TokenType.OPEN_TAG, name, sl, sc)
        for tok in attrs:
            self._tokens.append(tok)
        self._emit(TokenType.ATTR_NAME, "__verbatim__", sl, sc)
        self._emit(TokenType.VERBATIM, "".join(content_parts), content_line, content_col)
        self._emit(TokenType.CLOSE_TAG, name, self._line, self._col)

    # ------------------------------------------------------------------ #
    #  Lecture de texte nu                                                 #
    # ------------------------------------------------------------------ #

    def _read_text(self) -> None:
        start_line, start_col = self._line, self._col
        buf: List[str] = []
        while not self._eof():
            ch = self._peek()
            if ch == "^":
                break
            if ch == "_":
                # Regarde si c'est une balise fermante
                save = (self._pos, self._line, self._col)
                self._advance()
                name = self._read_name()
                if name and not self._eof() and self._peek() == ":":
                    # C'est une fermeture — remet le curseur
                    self._pos, self._line, self._col = save
                    break
                else:
                    # Texte libre : remet et lit le '_' comme texte
                    self._pos, self._line, self._col = save
                    buf.append(self._peek())
                    self._advance()
            else:
                buf.append(ch)
                self._advance()
        if buf:
            self._emit(TokenType.TEXT, "".join(buf), start_line, start_col)

    # ------------------------------------------------------------------ #
    #  Lecture d'une liste d'attributs                                    #
    # ------------------------------------------------------------------ #

    def _read_attribute_list(self) -> List[Token]:
        """Lit zéro ou plusieurs attributs name=''value'' et retourne les tokens."""
        tokens: List[Token] = []
        while True:
            # Saute les espaces/tabulations/retours de ligne simples
            if not self._skip_attr_separator():
                break
            # Vérifie qu'il y a bien un nom d'attribut
            if self._eof() or not (_is_letter(self._peek()) or self._peek() in ("_",)):
                # Restitue l'espace consommé — impossible proprement, on repart
                break
            al, ac = self._line, self._col
            name = self._read_attr_name()
            if not name:
                break
            tokens.append(Token(TokenType.ATTR_NAME, name, al, ac))
            # Signe '='
            if self._eof() or self._peek() != "=":
                raise LexerError(f"Attribut '{name}' : '=' attendu", al, ac)
            self._advance()
            # Ouverture ''
            if self._src[self._pos:self._pos + 2] != "''":
                raise LexerError(
                    f"Attribut '{name}' : \"''\" attendu après '='", self._line, self._col
                )
            self._advance(); self._advance()
            vl, vc = self._line, self._col
            value = self._read_until_quote_mark()
            tokens.append(Token(TokenType.ATTR_VALUE, value, vl, vc))
        return tokens

    def _skip_attr_separator(self) -> bool:
        """Saute un espace/tab ou un saut de ligne (mais pas \\n\\n).
        Retourne True si au moins un séparateur a été consommé."""
        if self._eof():
            return False
        ch = self._peek()
        # Un attribut commence après au moins un espace ou LF
        if ch not in (" ", "\t", "\n"):
            return False
        # Saute espaces/tabs
        consumed = False
        while not self._eof() and self._peek() in (" ", "\t"):
            self._advance()
            consumed = True
        # Optionnellement un saut de ligne (mais pas deux d'affilée)
        if not self._eof() and self._peek() == "\n":
            # Vérifie qu'on n'est pas sur \n\n
            if self._pos + 1 < len(self._src) and self._src[self._pos + 1] == "\n":
                return consumed  # double LF → pas un séparateur d'attribut
            self._advance()
            consumed = True
            # Espaces/tabs après le LF (alignement)
            while not self._eof() and self._peek() in (" ", "\t"):
                self._advance()
        return consumed

    # ------------------------------------------------------------------ #
    #  Helpers de lecture                                                  #
    # ------------------------------------------------------------------ #

    def _read_name(self) -> str:
        """Lit un nom de balise (element-name) incluant les '.' de namespace."""
        if self._eof():
            return ""
        ch = self._peek()
        # Reserved-name spéciaux : '_', '-', '#'
        if ch in ("-", "#"):
            self._advance()
            return ch
        if ch == "_":
            # Peut être '_' seul (happy-ending) ou début d'un user-name comme _foo
            # On lit le maximum
            self._advance()
            rest = ""
            while not self._eof() and _is_name_char(self._peek()):
                rest += self._peek()
                self._advance()
            return "_" + rest
        if not _is_letter(ch):
            return ""
        buf = ""
        while not self._eof() and _is_name_char(self._peek()):
            buf += self._peek()
            self._advance()
        return buf

    def _read_attr_name(self) -> str:
        """Lit un nom d'attribut (lettres, chiffres, '-', '_', '.')."""
        buf = ""
        while not self._eof():
            ch = self._peek()
            if _is_letter(ch) or _is_digit(ch) or ch in ("-", "_", "."):
                buf += ch
                self._advance()
            else:
                break
        return buf

    def _read_until_quote_mark(self) -> str:
        """Lit des caractères jusqu'au prochain digraphe \"''\"."""
        buf: List[str] = []
        while not self._eof():
            if self._src[self._pos:self._pos + 2] == "''":
                self._advance(); self._advance()  # consomme ''
                return "".join(buf)
            buf.append(self._peek())
            self._advance()
        raise LexerError(
            "Fin de fichier inattendue : delimiteur \"''\" manquant",
            self._line, self._col,
        )

    # ------------------------------------------------------------------ #
    #  Curseur                                                            #
    # ------------------------------------------------------------------ #

    def _peek(self) -> str:
        return self._src[self._pos]

    def _advance(self) -> str:
        ch = self._src[self._pos]
        self._advance_char(ch)
        return ch

    def _advance_char(self, ch: str) -> None:
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1

    def _eof(self) -> bool:
        return self._pos >= len(self._src)

    # ------------------------------------------------------------------ #
    #  Émission de tokens                                                 #
    # ------------------------------------------------------------------ #

    def _emit(self, ttype: TokenType, value: str, line: int, col: int) -> None:
        self._tokens.append(Token(ttype, value, line, col))
