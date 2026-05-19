"""
wriml.errors — Classes d'erreurs WRIML

Toutes les erreurs incluent la position (ligne/colonne) et un message
lisible par un humain, conforme aux exigences du brief (§ 3.8).
"""


class WRIMLError(Exception):
    """Erreur de base pour toutes les erreurs WRIML."""

    def __init__(self, message: str, line: int = 0, col: int = 0) -> None:
        self.wriml_message = message
        self.line = line
        self.col = col
        super().__init__(self._format())

    def _format(self) -> str:
        if self.line:
            return f"Erreur syntaxique ligne {self.line} colonne {self.col} :\n{self.wriml_message}"
        return f"Erreur : {self.wriml_message}"


class LexerError(WRIMLError):
    """Erreur levée par le lexer."""


class ParseError(WRIMLError):
    """Erreur levée par le parser."""

    def __init__(
        self,
        message: str,
        line: int = 0,
        col: int = 0,
        hint: str = "",
    ) -> None:
        self.hint = hint
        super().__init__(message, line, col)

    def _format(self) -> str:
        base = super()._format()
        if self.hint:
            return f"{base}\n{self.hint}"
        return base
