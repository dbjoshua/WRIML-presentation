
# WRIML 3.0
## WRiting Markup Language

> Markup for humans. As rigorous as XML, as fast as Markdown.

WRIML est un langage de balisage pensé pour l’écriture. Il vise un équilibre : **la rigueur de structure de XML + la vitesse de saisie de Markdown**.

*Repo officiel : https://github.com/dbjoshua/WRIML-presentation*

<a href="https://github.com/dbjoshua/WRIML-presentation">
  <img alt="WRIML 3.0" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMjAiIGhlaWdodD0iMjgiIHZpZXdCb3g9IjAgMCAxMjAgMjgiPjxzdHlsZT4udGV4dHtmb250OmJvbGQgMTNweCAtYXBwbGUtc3lzdGVtLEJsaW5rTWFjU3lzdGVtRm9udCxTZWdvZSBVSSxIZWx2ZXRpY2EsQXJpYWwsU2Fucy1zZXJpZjtmaWxsOiNmZmY7fTwvc3R5bGU+PHJlY3Qgd2lkdGg9IjEyMCIgaGVpZ2h0PSIyOCIgcng9IjQiIGZpbGw9IiMxRjI5MzciLz48cGF0aCBkPSJNMTIgNkw2IDEybDYgNiA2LTYtNi02eiIgZmlsbD0iIzI1NjNFQiIvPjx0ZXh0IHg9IjI4IiB5PSIxOSIgY2xhc3M9InRleHQiPldSSU1MIDMuMDwvdGV4dD48L3N2Zz4=" />
</a>

### Pourquoi WRIML 3.0 ?

WRIML a appris de ses erreurs :

| Version | Syntaxe | Problème |
|--- |:-: |:-- |
| **v1.0** | ` ^tag contenu _tag ` | Rigoureuse mais trop d’espaces obligatoires (espaces avant `^`, `_` et après le nom de la balise obligatoires). Lent, source d’erreurs. |
| **v2.0** | `^tag contenu_tag ` | on supprime l'espace avant `^` et on dit que tout ce qui n'est pas une lettre et un chiffre met automatiquement fin au nom de la balise (e.g. ```^tag content_tag.^tag2 content_tag2```:	Ergonomique mais ambiguë (e.g. ```^tag content_content``` est-ce que ça signifie "content" ou " content"?). On a perdu la rigueur. |
| **v3.0** |	`^tag:contenu_tag:` |	**Le compromis** : `:` démarre le contenu, `_tag:` le ferme. Rapide + sans ambiguïté. La v3.0 garde la rigueur de la v1.0 et l’ergonomie de la v2.0. | 

### Les 4 promesses

1. *Rigoureux* : Imbrication stricte. 0 ambiguïté. Validable par machine.
2. *Ergonomique* : 3 caractères clés `^ : _`. Peu de `Shift`. 40% moins de frappes que XML.
3. *Facile à apprendre* : 1 règle principale, 0 exception.
4. *Facile à lire* : Même un novice voit la structure. `^` ouvre, `_tag:` ferme.

### Syntaxe en 30 secondes

#### 1. Règle de base
`^balise:contenu_balise:`
*Exemple :*
```WRIML3.0
^doc markup=''3.0'':
^titre:Mon document WRIML_titre:

Ceci est un paragraphe nu. Pas besoin de l'encadrer avec la balise "p".

Un saut de ligne sépare deux paragraphes. Donc Ceci est un autre paragraphe.

Texte avec ^em:italique_em: dedans.
_doc:
```
#### 2. Les 3 cas spéciaux
|Type | Syntaxe	| Exemple |	Rôle |
|---|---|---|---|
| **Auto-fermant** |`^tag*`|	`^br*` `^hr*`|	Balise sans contenu|
|**Attributs**	|`^tag attr=''val'':..._tag:`	|`^img src=''logo.png'' alt=''Logo''*`	|Ajouter des infos. Toujours `''`|
|**Échapper `^`**	|`^chr code=''94''*`	|Pour écrire `^` littéral	Éviter conflit avec balise|

*Règle d’or* : Tout texte sans balise = paragraphe. Deux `\n\n` = nouveau paragraphe.

Structure de fichier : multi-racine autorisé

*Un fichier `.wriml` peut contenir 0, 1 ou N éléments à la racine.*  
Tu es libre de structurer ton fichier comme tu veux. WRIML est à la fois un format de document et un format de sérialisation.

*Exemple 1 : Document classique avec `^doc:`*
```WRIML3.0
^doc version=''1.2'' date=''2026-04-30'' markup=''3.0'':
^titre:Rapport_titre:
Contenu...
_doc:
```

*Exemple 2 : Flux multi-documents sans `^doc:`*
```WRIML3.0
^readme:
^titre:Archives Entretiens 2026_titre:
3 entretiens réalisés à Abidjan.
_readme:

^entretien id=''001'' date=''2026-04-15'':
^q:Parlez-moi de WRIML_q:
^r:Rigoureux et rapide_r:_entretien:

^entretien id=''002'' date=''2026-04-16'':
^q:Et la v3.0 ?_q:
^r:Le `:` change tout_r:_entretien:
```

Avantages : `git diff` propre, streaming, composition par `cat`. Tu codes tout un projet dans un seul `.wriml`.

### Que veut dire WRIML ?

*W R I M L = WRiting Markup Language*

- *WRiting* : Optimisé pour l’humain qui écrit. Chaque choix réduit la friction.
- *Markup Language* : Hérite de XML/HTML. Structuré, imbricable, validable.

<details>
<summary><strong>Balises prédéfinies & caractères de contrôle avancés</strong></summary>

WRIML est utilisable avec seulement `^tag:contenu_tag:`. Les balises ci-dessous sont des raccourcis pratiques pour cas avancés.

1. Élément racine et basiques

|Balise	|Syntaxe	|Rôle	|Exemple|
|---|---|---|---|
|**`doc` `document`**	|`^doc attr=''val'':..._doc:`|	Racine optionnelle. Peut porter les métadonnées du fichier	|`^doc markup=''3.0'' version=''1.0'':..._doc:`|
|**`p`**	|`^p:texte_p:`|	Paragraphe explicite	|`^p:Texte_p:` Optionnel : un texte nu est déjà un `p`|
|**`rem` `com` `-`**	|`^-:texte_-:`|	Commentaire|	`^-:TODO: à vérifier_-:` Ignoré au rendu|
|**`code`**	|`^code langage=''...''..._code:`|	Bloc de code	|`^code langage=''XML'':<tag>_code:`|

*Attributs de `^doc:` / `^document:` :*
- `markup=''WRIML3.0''` : Version de WRIML utilisée. Recommandé pour un document versionné.
- `version=''1.2''` : Version du document lui-même. Optionnel.
- `date=''2026-04-30''` : Date de création/révision. Optionnel. Format ISO 8601.

`^doc:` n’a aucun statut syntaxique spécial. C’est une convention. Tu peux avoir plusieurs `^doc:` ou zéro.

2. Caractères de contrôle : raccourcis one-shot

Ces balises sont des avatars de caractères Unicode de contrôle. Utiles pour parsing ou formats tabulaires.

| Balise |Équivaut à | Effet | Exemple |
|---|--- |--- |---|
| **`^gs*`** |	Group Separator `\x1D`	|Sépare 2 occurrences adjacentes du même élément |`^cellule:A^gs*B^gs*C_cellule:` = `^cellule:A_cellule:^cellule:B_cellule:^cellule:C_cellule:` |
|**`^eot*`**	|End of Transmission `\x04`	|Fin de document. Ignore tout ce qui suit. Uniquement à la racine	|`Texte^eot*Ce texte est ignoré` Comme `\endinput` LaTeX|
|**`^_*`**	|*happy ending*	|Termine la portée courante. Ignore le reste de la portée	|`^p:Début^_*Fin ignorée_p:` rend "Début"|

**À la racine, `^_*` = `^eot*`**
*Règle unifiée `^_*`* : `^_*` termine toujours la portée courante et ignore ce qui suit dans cette portée.  
1. Dans `^p:...^_*..._p:` → ferme le `p`, ignore le reste du `p`.  
2. À la racine → termine le document, ignore le reste du fichier. Sémantiquement identique à `^eot*`.

`^eot*` existe comme alias explicite pour "fin de document". `^_*` est l’outil universel. Tu retiens 1 seule balise.

`^eot*` ou `^_*` mal placé = erreur de syntaxe si une balise n’est pas fermée avant. `^_*` dans un élément évite ce piège car il ferme l’élément.

</details>

Spécification formelle
La grammaire EBNF de WRIML 3.0 sera bientôt disponible ici dans ce répertoire.

*Règle de structure* : `FichierWRIML = (Élément | Texte)_`  
Il n’y a pas de contrainte de racine unique.

### Roadmap v3.x
D’autres caractères de contrôle sont à l’étude pour v3.1+ : `FS` File Separator, `FF` Form Feed, etc. L’objectif : garder WRIML minimal mais extensible pour la sérialisation avancée.

*Philosophie* : Si ça peut s’écrire avec `^tag:contenu_tag:` on n’ajoute pas de raccourci. Les caractères de contrôle sont ajoutés uniquement s’ils résolvent une vraie douleur de saisie ou de parsing.

### Contribuer
Issues et PR bienvenues. WRIML 3.0 cherche l’équilibre parfait entre main et machine.

### Licence
MIT © https://github.com/dbjoshua
