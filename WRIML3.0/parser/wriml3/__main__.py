"""
wriml.__main__ — Interface CLI du parseur WRIML v3

Commandes disponibles :
    wriml parse    <fichier.wriml>   Affiche un résumé du document parsé
    wriml validate <fichier.wriml>   Valide la syntaxe (OK / erreur)
    wriml ast      <fichier.wriml>   Affiche l'AST complet en JSON

Exemples :
    python -m wriml parse    document.wriml
    python -m wriml validate document.wriml
    python -m wriml ast      document.wriml
    python -m wriml ast      document.wriml --indent 4
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, parse_file
from .errors import WRIMLError


def _cmd_parse(args: argparse.Namespace) -> int:
    try:
        doc = parse_file(args.file)
    except WRIMLError as exc:
        print(exc, file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable : {args.file}", file=sys.stderr)
        return 1

    n_nodes = len(doc.children)
    print(f"✓ Document parsé avec succès.")
    print(f"  Nœuds de premier niveau : {n_nodes}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        parse_file(args.file)
        print(f"✓ {args.file} : syntaxe valide.")
        return 0
    except WRIMLError as exc:
        print(f"✗ {args.file} : syntaxe invalide.\n{exc}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable : {args.file}", file=sys.stderr)
        return 1


def _cmd_ast(args: argparse.Namespace) -> int:
    try:
        doc = parse_file(args.file)
    except WRIMLError as exc:
        print(exc, file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable : {args.file}", file=sys.stderr)
        return 1

    indent = getattr(args, "indent", 2)
    print(doc.to_json(indent=indent))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wriml",
        description=f"Parseur minimal WRIML v3  (wriml-parser {__version__})",
    )
    parser.add_argument("--version", action="version", version=f"wriml-parser {__version__}")

    sub = parser.add_subparsers(dest="command", metavar="commande")
    sub.required = True

    # parse
    p_parse = sub.add_parser("parse", help="Parse un fichier WRIML et affiche un résumé.")
    p_parse.add_argument("file", metavar="fichier.wriml")
    p_parse.set_defaults(func=_cmd_parse)

    # validate
    p_val = sub.add_parser("validate", help="Valide la syntaxe d'un fichier WRIML.")
    p_val.add_argument("file", metavar="fichier.wriml")
    p_val.set_defaults(func=_cmd_validate)

    # ast
    p_ast = sub.add_parser("ast", help="Affiche l'AST complet en JSON.")
    p_ast.add_argument("file", metavar="fichier.wriml")
    p_ast.add_argument("--indent", type=int, default=2, metavar="N",
                       help="Indentation JSON (défaut : 2).")
    p_ast.set_defaults(func=_cmd_ast)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
