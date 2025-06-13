# Documentation de WRIML

## Introduction

WRIML (WRIting Markup Language) est un langage de balisage conçu pour simplifier la rédaction de documents textuels en fournissant une syntaxe claire et flexible.

## Principes de fonctionnement

WRIML repose sur plusieurs principes fondamentaux pour structurer les documents :

- **Utilisation de balises** : Les balises d'ouverture et de fermeture encadrent le contenu du document, permettant de délimiter les différents éléments.
  - Exemple : `^paragraph Ceci est un paragraphe _paragraph`
  
- **Simplicité syntaxique** : La syntaxe de WRIML est simple et intuitive, avec des balises représentées par des caractères spécifiques.
  - Exemple : `^heading Titre de section _heading`
  
- **Flexibilité** : Les utilisateurs peuvent définir leurs propres balises et éléments selon leurs besoins spécifiques, offrant une grande adaptabilité.
  - Exemple : `^note Ceci est une note _note`
  
- **Paragraphe par défaut** : Tout texte non encadré par une balise est considéré comme un paragraphe par défaut, ce qui simplifie la rédaction.
  - Exemple : Ceci est un paragraphe sans balise.

## Syntaxe de WRIML

La syntaxe de WRIML est simple et intuitive. Les principaux éléments à retenir sont :

- **Balises d'ouverture et de fermeture** : Les balises sont représentées par des caractères spécifiques, tels que `^` pour l'ouverture et `_` pour la fermeture.
  - Exemple : `^tag Contenu _tag`
  
- **Balises vides** : Les éléments vides sont représentés par une combinaison de caractères ouvrant et fermant, tels que `^_tag`.
  - Exemple : `^br _`
  
- **Attributs** : Les attributs sont définis en utilisant une syntaxe similaire à XML, avec le nom de l'attribut suivi de sa valeur entre guillemets.
  - Exemple : `^link_href="https://www.example.com" Lien _link`

## Remarques supplémentaires

Voici quelques remarques supplémentaires sur l'utilisation de WRIML :

- **Noms de balise flexibles** : Les noms de balise peuvent contenir des "-" comme séparateurs de mots (ex: ^nom-de-balise) ou utiliser la convention Camel Case (ex: ^NomDeBalise).
- **Balise par défaut pour les commentaires** : La balise par défaut pour les commentaires est "-", mais les utilisateurs peuvent définir leur propre balise de commentaire selon leurs préférences (ex: rem, com, note, comment, commentaire, etc.).
