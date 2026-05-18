# WRIML 3.0 — Spécification Formelle
**WRiting Markup Language — Version 3.0**  
Statut : Draft · Licence : MIT © https://github.com/dbjoshua

---

## 1. Introduction

WRIML (WRiting Markup Language) est un langage de balisage conçu pour l'écriture humaine. Il vise l'équilibre entre la rigueur structurelle de XML et la vitesse de saisie de Markdown.

### 1.1 Principes fondateurs

1. **Rigoureux** : imbrication stricte, zéro ambiguïté, validable par machine.
2. **Ergonomique** : 3 caractères clés (`^` `:` `_`), peu de `Shift`, ~40% moins de frappes que XML.
3. **Facile à apprendre** : une règle principale, zéro exception en usage courant.
4. **Facile à lire** : même un novice voit la structure. `^` ouvre, `_tag:` ferme.

### 1.2 Positionnement

WRIML est un langage de balisage indépendant. Il n'est pas un dialecte XML (il n'est pas parseable par un parseur XML), mais appartient à la même famille conceptuelle : arbre, imbrication, attributs, séparation structure/données.

---

## 2. Syntaxe de base (Couche 1)

La couche 1 couvre 99% des usages. Elle se compose de cinq formes et de trois caractères actifs principaux.

### 2.1 Caractères actifs

| Caractère | Rôle |
|---|---|
| `^` | Ouvre une balise |
| `:` | Démarre le contenu d'un élément |
| `_` | Ferme une balise (suivi du nom de la balise et de `:`) |

### 2.2 Les cinq formes syntaxiques

#### Forme 1 — Élément avec contenu
```
^balise:contenu_balise:
```
Exemple :
```
^titre:Mon document WRIML_titre:
```

#### Forme 2 — Élément avec attributs et contenu
```
^balise attr=''valeur'':contenu_balise:
```
Exemple :
```
^doc markup=''3.0'' version=''1.0'':contenu_doc:
```

#### Forme 3 — Élément auto-fermant (sans contenu)
```
^balise*
```
Exemple :
```
^br*
```

#### Forme 4 — Élément auto-fermant avec attributs
```
^balise attr=''valeur''*
```
Exemple :
```
^img src=''logo.png'' alt=''Logo''*
```

#### Forme 5 — Élément quoté (sucre syntaxique inline)
```
^balise''contenu''
^balise attr=''valeur'' ''contenu''
```
Exemples :
```
^em''mot en italique''
^lien href=''https://example.com'' ''texte du lien''
```

**Restrictions** : la forme quotée est réservée au contenu texte pur et court. Elle est interdite si le contenu contient des sous-éléments. `^` reste toujours actif à l'intérieur — utiliser `^cfx*` si nécessaire.

```
^em''mot en italique''            ✓  texte pur
^em''texte ^fort''gras''''        ✗  imbrication interdite
```

La forme canonique (`^balise:contenu_balise:`) reste toujours préférable pour la lisibilité et la maintenabilité.

### 2.3 Attributs

- Les valeurs d'attributs sont toujours encadrées par des doubles apostrophes `''`.
- `''` est un **digraphe atomique** : deux apostrophes U+0027 consécutives forment un seul token délimiteur. Le parseur ne les interprète jamais comme deux apostrophes simples séparées.
- Il ressemble visuellement à `"` mais n'est techniquement pas un guillemet — ce choix minimise l'inventaire des caractères actifs du langage.
- Une apostrophe simple `'` est toujours du texte libre, sans ambiguïté.
- Les caractères `"` sont donc libres à l'intérieur des valeurs.
- Plusieurs attributs sont séparés par un espace ou un retour à la ligne simple. Une ligne vide entre deux attributs est interdite.

```
^doc markup=''3.0'' version=''1.0'':          ✓  même ligne
^doc markup=''3.0''                            ✓  retour à la ligne simple
     version=''1.0'':

^doc markup=''3.0''                            ✗  ligne vide interdite

     version=''1.0'':
```

### 2.4 Noms de balises

Un nom de balise commence toujours par une lettre, suivie de lettres, chiffres, ou symboles selon la couche utilisée.

**Couche 1 — usage ordinaire** : lettres, chiffres, `-` et `_` uniquement.
```
^mon-tag:     ^nom_long:     ^titre2:
```

**Couche 2 — usage avancé** : symboles étendus supplémentaires autorisés : `@ $ £ ~ ` + & # |`. Réservés aux développeurs de sous-langages. Fortement déconseillés en usage courant.

Exclus définitivement (conflits de parsing) : `/` `\` et les caractères actifs WRIML (`^` `_` `:` `*` `''`).

### 2.5 Noms réservés

Certains noms de balises sont **réservés par la spécification WRIML**. Ils sont syntaxiquement valides mais leur sémantique est définie par la spec — l'utilisateur ne peut pas les redéfinir. Un parseur strict doit lever une erreur si un nom libre correspond à un nom réservé.

**Liste des noms réservés v3.0 :**

| Nom(s) | Rôle |
|---|---|
| `_` | Happy ending — ferme la portée courante |
| `-` `#` | Alias de commentaire |
| `doc` `document` | Racine de document |
| `tag-decl` | Bloc de déclaration de balises |
| `import` | Importation de ressources externes |
| `com` `cmt` `rem` `comment` | Commentaire verbatim |
| `p` `par` `paragraph` | Paragraphe |
| `code` | Bloc de code verbatim |
| `cfx` | Échappement de `^` |
| `us` `underscore` | Échappement de `_` |
| `dash` | Échappement de `-` |
| `chr` `char` | Insertion de caractère Unicode |
| `gs` | Group Separator |
| `eot` | End of Transmission |

> **Règle** : un utilisateur qui tente de définir une balise `^code:` dans son propre sens, par exemple, obtiendra un comportement non défini. Les noms réservés sont la propriété de la spécification WRIML.

**Préfixe conventionnel recommandé :**

`decl` est un préfixe conventionnel recommandé par la spec pour les éléments de déclaration (`^decl.tag*`, `^decl.attr*`). Contrairement aux noms réservés, il n'est **pas verrouillé** — un développeur peut choisir un autre préfixe. Le parseur ne lui attribue aucun comportement spécial. Il est documenté ici comme convention, non comme contrainte.

### 2.6 Texte nu

Tout texte non encadré par une balise est un **nœud texte** valide à la racine ou dans un élément. Deux sauts de ligne consécutifs (`\n\n`) délimitent deux nœuds texte distincts (paragraphes). Le parseur ne les enveloppe pas implicitement dans `^p:` — le texte nu est un nœud texte flottant dans l'arbre.

```
Ceci est un nœud texte.

Ceci est un autre nœud texte séparé par \n\n.
```

### 2.7 Imbrication

Les éléments s'imbriquent strictement. Toute balise ouverte doit être fermée dans la portée où elle a été ouverte. Les croisements de balises sont interdits.

```
^p:Texte avec ^em:italique_em: dedans._p:   ✓
^p:^em:croisé_p:_em:                         ✗
```

### 2.8 Structure de fichier

Un fichier `.wriml` peut contenir zéro, un ou plusieurs éléments à la racine (multi-racine autorisé). Il n'y a pas de contrainte de racine unique.

```
FichierWRIML = (Élément | TexteNu)*
```

---

## 3. Conventions de balisage

Cette section décrit les conventions recommandées pour structurer un document WRIML. Ces conventions ne sont pas des règles syntaxiques — un document qui ne les suit pas reste valide. Elles constituent le bon usage commun, conçu pour faciliter la lisibilité et l'interopérabilité.

### 3.1 Structure du document

#### Une règle, trois usages émergents

La règle fondamentale est simple : `document = { node }`. Zéro, un ou plusieurs éléments à la racine, du texte nu entre eux ou seul — tout est valide. Cette décision, combinée au fait que le texte nu est un nœud à part entière, a une conséquence inattendue : elle fait émerger naturellement trois usages distincts sans qu'aucune règle supplémentaire soit nécessaire.

**Usage 1 — Notes rapides**

Un fichier vide est un document WRIML valide. Un fichier contenant uniquement du texte brut l'est tout autant. On peut annoter ce qui semble pertinent sur le moment sans planifier la structure globale :

```
Voici mes notes du jour.

^em:Cette idée est importante_em: à retenir.

On verra plus tard comment structurer tout ça.
```

Texte nu, une balise inline, pas de racine, pas de `^doc:` — document parfaitement valide. WRIML s'efface derrière le contenu. Idéal pour des notes rapides, des annotations légères, ou tout contexte où la structure vient après le contenu.

**Usage 2 — Import et composition**

Un fragment WRIML est lui-même un document WRIML valide. Il peut donc être inséré dans un document plus grand sans manipulation de structure — pas besoin de le déshabiller d'une racine artificielle avant de l'inclure ailleurs. C'est une simple concaténation, et le résultat est toujours un document valide. Un mécanisme formel d'importation (`^import*`) est documenté en section 3.5.

**Usage 3 — Flux de données**

Plusieurs entrées indépendantes dans un seul fichier, sans racine enveloppante :

```
^entretien id=''001'' date=''2026-04-15'':..._entretien:
^entretien id=''002'' date=''2026-04-16'':..._entretien:
^entretien id=''003'' date=''2026-04-17'':..._entretien:
```

Chaque entrée est un arbre indépendant. Un parseur peut les traiter en flux sans charger tout le fichier en mémoire — particulièrement utile pour les corpus linguistiques, les archives, ou les pipelines de données.

Ces trois usages ne sont pas des fonctionnalités ajoutées — ce sont des conséquences directes de `document = { node }`.

#### Du libre au structuré

WRIML ne force pas de niveau de rigueur. Le spectre va du plus libre au plus formel selon les besoins du projet :

| Niveau | Structure | Usage typique |
|---|---|---|
| Texte brut annoté | Aucune racine, balises optionnelles | Notes, brouillons, annotations rapides |
| Document simple | `^doc:` comme racine unique | Articles, rapports, documents partagés |
| Document structuré | `^doc:` + `^tag-decl:` + hiérarchie pensée | Corpus, archives, publications, schémas |

Pour des projets ambitieux destinés à être partagés, archivés ou validés, la rigueur structurelle est fortement recommandée. Mais cette rigueur est un choix, pas une contrainte imposée par le langage.

#### La balise `^doc:`

`^doc:` (ou `^document:`) est la racine conventionnelle d'un document structuré. Elle est optionnelle mais recommandée dès qu'un document a vocation à être partagé, archivé, ou validé.

```
^doc type=''rapport'' markup=''3.0'' version=''1.0'' date=''2026-05-17'':
...
_doc:
```

L'attribut `type` permet de spécifier le type de document. `^doc type=''manuscrit'':` est sémantiquement équivalent à `^manuscrit:` — c'est une question de style et de convention propre au projet.

### 3.2 Balises prédéfinies

Les balises prédéfinies sont des **noms réservés** par la spécification WRIML. Elles ne doivent jamais être redéfinies par l'utilisateur — leur sémantique est fixée par la spec et un parseur strict lèvera une erreur en cas de redéfinition. Voir la section **2.5** pour la liste exhaustive des noms réservés.

| Balise | Rôle | Détail |
|---|---|---|
| `^doc:` `^document:` | Racine optionnelle, porte les métadonnées | Voir section 3.3 |
| `^titre:` | Titre principal | — |
| `^p:` `^par:` `^paragraph:` | Paragraphe explicite — trois alias équivalents | — |
| `^em:` | Emphase (italique) | — |
| `^fort:` | Fort (gras) | — |
| `^code:` | Bloc de code — environnement verbatim | Voir section 4 |
| `^rem:` `^com:` `^cmt:` `^-:` `^#:` `^comment:` | Commentaire — environnement verbatim, ignoré au rendu | Voir section 4 |
| `^tag-decl:` | Bloc de déclaration de balises | Voir section 3.4 |

### 3.3 Attributs de `^doc:`

| Attribut | Rôle | Statut |
|---|---|---|
| `type=''xxx''` | Type de document (`rapport`, `corpus`, `manuscrit`, etc.) | Recommandé |
| `markup=''3.0''` | Version de WRIML utilisée | Recommandé |
| `version=''1.2''` | Version du document | Optionnel |
| `date=''2026-04-30''` | Date de création/révision — format ISO 8601 | Optionnel |

### 3.4 Déclaration de balises — `^tag-decl:`

`^tag-decl:` est un bloc optionnel, placé en tête de document, qui liste les balises utilisées dans le fichier. Il sert de documentation embarquée — le lecteur humain comprend immédiatement le vocabulaire du document sans devoir chercher une référence externe.

> **Règle d'or** : fortement recommandé dès qu'un document utilise des balises non-standard ou spécifiques à un domaine.

#### Structure

```
^doc version=''1.0'' date=''2026-05-02'' markup=''wriml 3.0'':
^tag-decl:
  ^#: Déclaration des balises _#:
  ^decl.tag name=''doc''   meaning=''document''*
  ^decl.tag name=''titre'' meaning=''titre principal''*
  ^decl.tag name=''mb''    meaning=''morphème''    ns=''ling''*
  ^decl.tag name=''gl''    meaning=''glose''       ns=''ling''
            description=''traduction morphème par morphème''*
  ^decl.tag name=''gr''    meaning=''catégorie grammaticale'' ns=''ling''*
  ^decl.tag name=''auteur''     meaning=''auteur du document''*
  ^decl.tag name=''compositeur'' meaning=''compositeur associé''*

  ^#: Déclaration des attributs _#:
  ^decl.attr name=''id'' meaning=''identifiant unique du nœud''*
  ^#: ↑ pas de tag-list : attribut universel, applicable à toutes les balises _#:

  ^decl.attr name=''nom'' meaning=''nom de la personne''
             tag-list=''auteur compositeur''*
  ^#: ↑ tag-list explicite : restreint à auteur et compositeur _#:

  ^decl.attr name=''type'' meaning=''type de catégorie''
             description=''valeurs : pos, nb, pers, temps''
             tag-list=''gr''*
_tag-decl:

^titre:Mon document_titre:
...
_doc:
```

#### Attributs de `^decl.tag*`

| Attribut | Obligatoire | Rôle |
|---|---|---|
| `name=''xxx''` | **Oui** | Nom exact de la balise déclarée |
| `meaning=''xxx''` | **Oui** | Sens court, lisible par un humain |
| `ns=''xxx''` | Si namespace utilisé | Préfixe namespace associé |
| `description=''xxx''` | Non | Explication longue, usage, contraintes |

#### Sous-élément `^decl.attr*` — déclaration des attributs d'une balise

`^decl.attr*` déclare un attribut et l'associe explicitement à une ou plusieurs balises via `tag-list`. Il peut apparaître n'importe où dans `^tag-decl:` — son lien aux balises est porté par `tag-list`, pas par sa position.

| Attribut | Obligatoire | Rôle |
|---|---|---|
| `name=''xxx''` | **Oui** | Nom de l'attribut |
| `tag-list=''xxx yyy''` | **Voir avertissement** | Balises auxquelles cet attribut s'applique, séparées par des espaces |
| `meaning=''xxx''` | Non | Sens court |
| `description=''xxx''` | Non | Valeurs possibles, format, contraintes |

> ⚠️ **`tag-list` absent = attribut universel.** Un `^decl.attr*` sans `tag-list` déclare un attribut applicable à **toutes** les balises du document. C'est rarement l'intention — toujours vérifier qu'un `tag-list` manquant est bien intentionnel.

Exemples :

```
^#: Attribut restreint à deux balises _#:
^decl.attr name=''nom'' meaning=''nom de la personne''
           tag-list=''auteur compositeur''*

^#: Attribut universel — intentionnel et explicite _#:
^decl.attr name=''id'' meaning=''identifiant unique du nœud''*
```

Un même attribut peut être déclaré plusieurs fois avec des `tag-list` différents si les descriptions varient selon le contexte.

#### Règles

- `^tag-decl:` est **optionnel** mais fortement recommandé dès que le document utilise des balises non-standard ou spécifiques à un domaine.
- `^tag-decl:` se place toujours **immédiatement après l'ouverture de `^doc:`**, avant tout contenu.
- `^decl.tag*` et `^decl.attr*` sont des éléments auto-fermants — ils ne portent pas de contenu, uniquement des attributs.
- Le lien entre `^decl.attr*` et ses balises est porté par `tag-list`, pas par la position dans le bloc.
- `^decl.attr*` sans `tag-list` déclare un attribut universel applicable à toutes les balises — utiliser avec précaution et intentionnellement.
- Le bloc `^tag-decl:` est ignoré au rendu — c'est de la métadonnée pure.

### 3.5 Importation de ressources — `^import*`

#### Pourquoi `^import*` est dans le cœur

`^import*` est un mécanisme d'importation de ressources externes. Il est défini dans le cœur de WRIML — pas dans un dialecte spécifique — parce que le besoin est universel : tout projet WRIML de taille réelle aura besoin de référencer des fichiers externes, qu'il s'agisse de fragments WRIML, de palettes de couleurs, d'images, ou de schémas. Laisser ce mécanisme aux dialectes signifierait que chaque dialecte réinvente sa propre syntaxe (`^include*`, `^use*`, `^ref*`) au détriment de l'interopérabilité.

`^import*` bénéficie directement de la philosophie multi-racine de WRIML : un fragment WRIML est lui-même un document WRIML valide. L'importer revient à une concaténation sémantique — le résultat est toujours un document valide.

#### Syntaxe

`^import*` est un élément auto-fermant. L'attribut `src` est obligatoire.

```
^import src=''chemin/vers/fichier.wriml''*
^import src=''ressource.ext'' type=''image''*
^import src=''schema.wriml'' as=''ns''*
```

#### Attributs de `^import*`

| Attribut | Obligatoire | Rôle |
|---|---|---|
| `src=''xxx''` | **Oui** | Chemin ou URI de la ressource à importer |
| `type=''xxx''` | Non | Type de la ressource si non inférable de l'extension |
| `as=''xxx''` | Non | Alias namespace — lie le contenu importé à un préfixe |

#### Valeurs standardisées de `type`

| Valeur | Rôle |
|---|---|
| `wriml` | Fragment WRIML (défaut si extension `.wriml`) |
| `image` | Image matricielle ou vectorielle |
| `code` | Fichier de code source — traité comme verbatim |
| `texte` | Fichier texte brut — traité comme nœud texte |
| `schema` | Schéma WRIML définissant un dialecte |
| `palette` | Palette de couleurs UCP (`.ucp`) |

D'autres valeurs peuvent être définies par les dialectes.

#### Résolution des chemins

- **Chemin relatif** : résolu depuis le répertoire du fichier WRIML courant.
- **Chemin absolu** : résolu depuis la racine du système de fichiers.
- **URI distante** : autorisée syntaxiquement en v3.0, support optionnel pour les parseurs. Un parseur qui ne supporte pas les URI distantes doit lever un **avertissement**, pas une erreur.

```
^import src=''fragments/intro.wriml''*           ^#: relatif _#:
^import src=''/projets/shared/header.wriml''*    ^#: absolu _#:
^import src=''https://example.com/schema.wriml''* ^#: URI distante _#:
```

#### L'attribut `as` — import avec alias namespace

`as=''xxx''` associe le contenu importé à un préfixe namespace. Cela permet d'utiliser les balises du fichier importé sans collision avec le vocabulaire du document courant.

```
^import src=''ling-schema.wriml'' as=''ling''*
```

Après cet import, les balises définies dans `ling-schema.wriml` sont accessibles sous le préfixe `ling` :

```
^ling.mb:tralE jE O_ling.mb:
^ling.gl:habit ^ling.gr''foc''_ling.gl:
```

Sans `as`, le contenu importé est inséré à plat dans le document courant — les noms de balises sont directement accessibles, avec un risque de collision si les vocabulaires se chevauchent.

#### Niveaux de conformité des parseurs

`^import*` est dans le cœur syntaxique mais son implémentation est graduée :

| Niveau | Comportement |
|---|---|
| **Basique** | Reconnaît `^import*` syntaxiquement, l'ignore au parsing. Avertissement recommandé. |
| **Local** | Résout les chemins relatifs et absolus locaux. Erreur sur URI distante. |
| **Complet** | Résout chemins locaux et URI distantes. Gère les imports circulaires. |

Un parseur doit déclarer son niveau de conformité pour `^import*`. Un parseur **basique** qui ignore silencieusement `^import*` sans avertissement n'est pas conforme.

#### Imports circulaires

Un import circulaire — `a.wriml` importe `b.wriml` qui importe `a.wriml` — est une **erreur formelle**. Un parseur de niveau **local** ou **complet** doit détecter les cycles et lever une erreur avec le chemin du cycle identifié.

#### Exemples complets

**Import d'un fragment WRIML**
```
^doc markup=''3.0'' type=''rapport'':
^import src=''fragments/entete.wriml''*
^import src=''fragments/introduction.wriml''*

^titre:Corps du rapport_titre:
...
_doc:
```

**Import d'une palette UCP avec alias**
```
^doc markup=''3.0'' type=''publication'':
^import src=''../palettes/corporate.ucp'' type=''palette'' as=''pal''*

^#: Les couleurs de la palette sont accessibles sous ^pal.couleur _#:
...
_doc:
```

**Import d'un schéma linguistique**
```
^doc markup=''3.0'' type=''corpus'':
^import src=''schemas/ling-schema.wriml'' type=''schema'' as=''ling''*
^tag-decl:
  ^#: Les balises du schéma importé sont documentées dans ling-schema.wriml _#:
  ^decl.tag name=''data'' meaning=''entrée de corpus''*
_tag-decl:

^data:
^ling.mb:tralE jE O fa-li O_ling.mb:
^ling.gl:habit ^ling.gr''foc''^ling.gr''3''^ling.gr''sg''
  prendre-^ling.gr''pas''.^ling.gr''perf''_ling.gl:
^ft:C'est un habit qu'il a pris_ft:
_data:
_doc:
```

**Import de code source**
```
^doc markup=''3.0'' type=''documentation'':
^titre:Documentation de l'API_titre:

^p:Voici l'implémentation de référence :_p:
^import src=''src/parser.rs'' type=''code''*
_doc:
```

#### Règles récapitulatives

- `src` est obligatoire — `^import*` sans `src` est une erreur de syntaxe.
- `type` est optionnel — inferable de l'extension dans la plupart des cas.
- `as` est optionnel — recommandé pour éviter les collisions de noms.
- Les chemins relatifs et absolus locaux sont supportés par tous les parseurs de niveau **local** et supérieur.
- Les URI distantes sont syntaxiquement valides mais le support est optionnel en v3.0.
- Les imports circulaires sont une **erreur formelle**.
- `^import*` peut apparaître n'importe où dans un document — à la racine ou dans un élément.

---

## 4. Caractères de contrôle (Couche 1 avancée)

Ces balises sont des raccourcis pour des caractères Unicode de contrôle. Elles font partie de la couche 1 mais sont à usage avancé — inutiles en écriture ordinaire.

| Balise | Équivaut à | Rôle | Exemple |
|---|---|---|---|
| `^gs*` | Group Separator `\x1D` | Sépare deux occurrences adjacentes du même élément | `^cell:A^gs*B^gs*C_cell:` |
| `^eot*` | End of Transmission `\x04` | Fin de document, ignore tout ce qui suit. Uniquement à la racine | `Texte^eot*Ignoré` |
| `^_*` | *happy ending* | Termine la portée courante, ignore le reste de cette portée | `^p:Début^_*Ignoré_p:` |

**Règle unifiée de `^_*`** :
- Dans un élément : ferme l'élément, ignore le reste de sa portée.
- À la racine : équivalent à `^eot*`, termine le document.

`^eot*` et `^_*` à la racine sont sémantiquement identiques. `^eot*` existe comme alias explicite pour la lisibilité.

---

## 5. Échappement

La philosophie d'échappement de WRIML est cohérente : **tout est élément**, y compris l'échappement. Il n'existe pas d'opérateur d'échappement hors-syntaxe (pas de `\`).

`^` est toujours un caractère actif. Un `^` non suivi d'un nom de balise valide est une **erreur de syntaxe** — jamais du texte libre. Pour insérer `^` littéral dans un document, `^cfx*` est obligatoire.

| Balise | Rôle | Exemple |
|---|---|---|
| `^cfx*` | Insère `^` littéral (*circumflex*) | `Prix^cfx*20` → `Prix^20` |
| `^us*` `^underscore*` | Insère `_` littéral | `^us*` → `_` |
| `^dash*` | Insère `-` littéral | `^dash*` → `-` |
| `^chr code=''N''*` | Insère le caractère Unicode de point de code décimal N | `^chr code=''94''*` → `^` |

`^cfx*`, `^us*` et `^dash*` sont les raccourcis recommandés pour les caractères les plus courants. `^chr*` est l'outil général pour tout caractère Unicode.

---

## 6. Namespaces (Couche 2)

Les namespaces sont **optionnels**. Ils ne doivent être utilisés qu'en cas de besoin réel : collision de noms de balises, interopérabilité formelle, développement d'un sous-langage WRIML.

> **Règle d'or** : si tu n'as pas de collision, n'utilise pas de namespace.

### 6.1 Namespace informel (usage recommandé)

Un préfixe suivi d'un point `.` précède le nom de la balise :

```
^prefix.balise:contenu_prefix.balise:
```

Exemple :
```
^doc.titre:Rapport médical_doc.titre:
^med.titre:Diagnostic_med.titre:
```

**Recommandation** : maximum 2 segments (`^ns.balise:`). Des segments supplémentaires sont syntaxiquement autorisés mais déconseillés.

Le préfixe est libre — aucune déclaration n'est requise. Il doit être lisible et significatif pour l'auteur et le lecteur.

### 6.2 Namespace formel (usage exceptionnel)

Pour les cas nécessitant une résolution formelle vers une URI (validation automatique, interopérabilité inter-systèmes), une déclaration explicite est possible via l'attribut réservé `wrimlns.xxx` :

```
^doc wrimlns.doc=''https://monsite.com/schema'' 
     wrimlns.med=''https://medical.org/wriml'':
...
_doc:
```

`wrimlns.xxx` est un **mot-clé composé réservé**. Le point fait partie intégrante du token — ce n'est pas une généralisation du point aux attributs ordinaires. Les attributs ordinaires n'utilisent jamais le point.

Cette syntaxe est **fortement déconseillée** en usage courant. Elle est documentée ici pour les développeurs de sous-langages et les pipelines de données formels.

---

## 7. Mots-clés système (Couche 2)

### 7.1 Principe

Tout attribut dont le nom commence par un **préfixe système** suivi d'un point est un mot-clé système réservé. Ces attributs font partie de la couche 2 — ils sont disponibles mais leur usage doit rester exceptionnel, à la manière des fichiers cachés d'un système d'exploitation : présents, documentés, mais non destinés à l'usage quotidien.

### 7.2 Préfixe réservé WRIML

Le préfixe `wriml` est réservé à la spécification officielle WRIML. Aucun développeur tiers ne doit définir d'attributs commençant par `wriml`.

| Mot-clé | Rôle |
|---|---|
| `wrimlns.xxx=''uri''` | Déclaration formelle de namespace |

Des mots-clés supplémentaires pourront être ajoutés dans les versions v3.x.

### 7.3 Préfixes tiers

Les développeurs créant un sous-langage ou une extension WRIML peuvent définir leurs propres préfixes système :

```
^doc whtml.charset=''utf-8'':..._doc:
```

| Préfixe | Propriétaire suggéré | Exemple |
|---|---|---|
| `wriml` | Spécification officielle WRIML | `wrimlns.doc=''uri''` |
| `whtml` | Développeur d'un remix HTML | `whtml.charset=''utf-8''` |
| `wsvg` | Développeur d'un remix SVG | `wsvg.viewport=''0 0 100 100''` |

Aucun registre central n'est imposé en v3.0. Un registre communautaire est envisagé pour une version ultérieure.

---

## 8. Résumé des deux couches

| | Couche 1 — Surface | Couche 2 — Système |
|---|---|---|
| **Public** | Tous les utilisateurs | Développeurs de sous-langages, pipelines formels |
| **Formes syntaxiques** | Formes 1 à 5, `^tag:` `^tag attr=''val'':` `^tag*` `^tag''contenu''` | Namespaces, mots-clés `wriml`, préfixes tiers |
| **Symboles dans les noms** | `-` `_` uniquement | `@ $ £ ~ ` + & # \|` |
| **Déclaration namespace** | Aucune | `wrimlns.xxx=''uri''` |
| **Philosophie** | Toujours utiliser | N'utiliser qu'en cas d'absolue nécessité |

---

## 9. Exemples complets

### Document classique
```
^doc markup=''3.0'' version=''1.0'' date=''2026-05-01'':
^titre:Rapport annuel_titre:

Introduction du rapport.

^em:Note importante_em: : relire avant publication.
_doc:
```

### Forme quotée (inline)
```
Texte avec ^em''italique'' et ^fort''gras'' inline.
^lien href=''https://example.com'' ''texte du lien''
```

### Flux multi-documents
```
^entretien id=''001'' date=''2026-04-15'':
^q:Parlez-moi de WRIML_q:
^r:Rigoureux et rapide_r:
_entretien:

^entretien id=''002'' date=''2026-04-16'':
^q:Et la v3.0 ?_q:
^r:Le `:` change tout_r:
_entretien:
```

### Avec namespace informel
```
^doc.rapport titre=''Analyse'':
^doc.section:Introduction_doc.section:
^med.diagnostic code=''A01'':Fièvre typhoïde_med.diagnostic:
_doc.rapport:
```

### Échappement
```
Prix HT ^cfx* TVA = Prix TTC
Note^us*de^us*bas : voir référence^dash*1
```

---

## 10. Roadmap

| Version | Fonctionnalité prévue |
|---|---|
| v3.0 | Spécification actuelle, Grammaire EBNF publiée |
| v3.1 | registre de préfixes tiers, nouveaux caractères de contrôle (`FS`, `FF`) |
| v3.2+ | Nouveaux mots-clés système selon besoins identifiés |

**Philosophie d'extension** : si ça peut s'écrire avec `^tag:contenu_tag:`, on n'ajoute pas de raccourci. Toute addition doit résoudre une vraie douleur de saisie ou de parsing.

---

*Spécification WRIML 3.0 · MIT © https://github.com/dbjoshua*
