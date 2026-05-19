# wriml-parser

Parseur minimal officiel du langage **WRIML v3** (WRiting Markup Language).

> As fast as Markdown, as rigorous as XML.

---

## Installation

```bash
pip install .
# ou en mode développement :
pip install -e .
```

Aucune dépendance externe — stdlib Python uniquement.

---

## Usage Python

```python
from wriml import parse, parse_file

# Depuis une chaîne
doc = parse("^section titre=''Introduction'':^p:Bonjour_p:_section:")

# Depuis un fichier
doc = parse_file("document.wriml")

# Accès à l'AST
doc.children          # liste des nœuds de premier niveau
doc.to_json()         # sérialisation JSON (str)
```

---

## CLI

```bash
# Résumé du document
wriml parse document.wriml

# Validation syntaxique
wriml validate document.wriml

# AST complet en JSON
wriml ast document.wriml
wriml ast document.wriml --indent 4
```

Ou sans installation :

```bash
python -m wriml parse document.wriml
```

---

## Architecture

```
wriml/
├── __init__.py      API publique  (parse, parse_file)
├── __main__.py      CLI
├── tokens.py        Types de tokens (TokenType, Token)
├── lexer.py         Lexer  : source str → List[Token]
├── parser.py        Parser : List[Token] → DocumentNode (AST)
├── ast.py           Nœuds AST (DocumentNode, ElementNode, TextNode, …)
└── errors.py        LexerError, ParseError, WRIMLError
```

Pipeline :

```
Source .wriml
    ↓  Lexer
List[Token]
    ↓  Parser
DocumentNode (AST)
    ↓  .to_json()
JSON
```

---

## Structure de l'AST

### DocumentNode

```json
{
  "type": "document",
  "children": [ ... ]
}
```

### ElementNode

```json
{
  "type": "element",
  "name": "section",
  "kind": "paired",
  "attributes": { "titre": "Introduction" },
  "children": [ ... ],
  "pos": { "line": 1, "col": 1 }
}
```

`kind` peut valoir :
- `"paired"` — balise ouvrante + fermante (`^tag:…_tag:`)
- `"empty"` — auto-fermant (`^tag*`)
- `"quoted"` — forme inline (`^tag''contenu''`)
- `"verbatim"` — bloc code/commentaire (`^code:…_code:`)
- `"escape"` — élément d'échappement (`^cfx*`, `^us*`, …)

### TextNode

```json
{ "type": "text", "text": "Bonjour le monde" }
```

### ControlNode

```json
{ "type": "control", "control": "gs" }
```

(`control` ∈ `"happy_ending"`, `"eot"`, `"gs"`)

---

## Messages d'erreur

Les erreurs incluent toujours la ligne et la colonne :

```
Erreur syntaxique ligne 18 colonne 4 :
Balise fermante '_section:' inattendue.
Balise ouverte attendue : '_p:'
```

---

## Tests

```bash
pytest tests/ -v
```

---

## Exemple complet

```wriml
^doc markup=''3.0'' date=''2026-05-02'':

  ^titre:Analyse morphologique_titre:

  ^data:
    ^mb:tralE jE O fa-li O_mb:
    ^gl:habit ^gr''foc'' ^gr''3''^gr''sg''
      prendre-^gr''pas''.^gr''perf''_gl:
    ^ft:C'est un habit qu'il a pris_ft:
  _data:

_doc:
```

---

## Licence

MIT — voir [dbjoshua/WRIML](https://github.com/dbjoshua/WRIML)
