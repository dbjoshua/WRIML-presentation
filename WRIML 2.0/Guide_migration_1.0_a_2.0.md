# Guide de migration : WRIML 1.0 ➔ WRIML 2.0

> Version de WRIML cible : **2.0**
> Dernière mise à jour : 13 juin 2025

---

## Introduction

Ce guide explique les différences principales entre **WRIML 1.0** et **WRIML 2.0**, en se concentrant sur les changements de syntaxe, de grammaire, et de conventions d'écriture. Il fournit des exemples concrets pour faciliter la migration des documents.

---

## Table des matières

1. [Balises : suppression des espaces obligatoires](#1-balises--suppression-des-espaces-obligatoires)
2. [Nouveaux caractères réservés et échappement explicite](#2-nouveaux-caractères-réservés-et-échappement-explicite)
3. [Changement de syntaxe des attributs](#3-changement-de-syntaxe-des-attributs)
4. [Nouveaux éléments primitifs](#4-nouveaux-éléments-primitifs)
5. [Alias et racines logiques](#5-alias-et-racines-logiques)
6. [Compatibilité ascendante et astuces de migration](#6-compatibilité-ascendante-et-astuces-de-migration)

---

## 1. Balises : suppression des espaces obligatoires

### WRIML 1.0

```wriml
^titre Ceci est un titre _titre
```

Les espaces étaient obligatoires avant/après les balises.

### WRIML 2.0

```wriml
^titre Ceci est un titre_titre
```

Les espaces ne sont plus obligatoires. Toutefois, ils peuvent être conservés sans effet secondaire.

---

## 2. Nouveaux caractères réservés et échappement explicite

### Caractères réservés

* `^` (début de balise)
* `_` (fin de balise)
* `:` (séparateur d'attribut)

### Mécanisme d'échappement

* `^_^` ➔ insère un `^` littéral
* `^__` ➔ insère un `_` littéral
* `^_:` ➔ insère un `:` littéral

### Exemples

```wriml
^phraseCeci est un exemple de ^_^balise^_^ littérale._phrase
```

---

## 3. Changement de syntaxe des attributs

### WRIML 1.0

```wriml
^mot_lang="fr"bonjour_mot
```

### WRIML 2.0

```wriml
^mot:lang="fr"bonjour_mot
```

Les attributs sont maintenant introduits par `:`. On tolère `: ` (deux caractères) sans ambigüité.

---

## 4. Nouveaux éléments primitifs

* `^-`, `^rem`, `^com` : commentaire
* `^code:lang="..." ... _code` : bloc de code (avec détection de langage)
* `^verb:lang="..." ... _verb` : bloc de texte à ne pas interpréter (verbatim)
* `^doc:type="..." ... _doc` : racine générique de document

### Exemple complet

```wriml
^doc:type="datafile":markup="wriml-2.0":version="2.0":date="13-06-2025"
^titreUn exemple de document_titre
^code:lang="Markdown"
# Un titre
_code
_doc
```

---

## 5. Alias et racines logiques

* `^datafile..._doc` est équivalent à `^doc:type="datafile"..._doc`
* `^rem`, `^com`, `^-` sont synonymes de l'élément commentaire

---

## 6. Compatibilité ascendante et astuces de migration

### Compatibilité

Les documents WRIML 1.0 sont **non valides** en 2.0 sans ajustement, mais la transformation est systématique :

### Méthodologie de migration automatique

1. Rechercher les balises avec espaces `^nom ` et `_nom`
2. Supprimer les espaces (si on est certain que ce n'est pas un contenu)
3. Remplacer `_` entre nom d'élément et attributs par `:`
4. Ajouter échappement explicite aux `^`, `_`, `:` dans le texte si besoin

### Outils de migration

Un script Python peut être écrit pour automatiser la majorité de ces transformations, suivant l'intérêt pour ce système.

---

## Notes finales

WRIML 2.0 apporte une syntaxe plus naturelle, plus robuste et plus facile à valider automatiquement. Bien que plus rigoureuse, elle reste tolérante là où la lisibilité et la fluidité de saisie priment.

Pour plus de précision, consulter la [spécification formelle WRIML 2.0](github.com/dbjoshua/WRIML-presentation/WRIML%202.0/WRIML_2.0_specification.ebnf).
