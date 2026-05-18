# WRIML 3.0 — Grammaire EBNF
**WRiting Markup Language — Version 3.0**
Statut : Draft · Licence : MIT © https://github.com/dbjoshua

---

## Conventions EBNF

```
=          définition
|          alternative
[ ]        optionnel (0 ou 1)
{ }        répétition (0 ou N)
( )        groupement
" "        terminal littéral
(* *)      commentaire
,          concaténation
```

---

## Grammaire

```ebnf
(* ═══════════════════════════════════════════════════════════ *)
(*  DOCUMENT                                                   *)
(* ═══════════════════════════════════════════════════════════ *)

document
  = { node } ;
  (* Zéro, un ou plusieurs nœuds — multi-racine autorisé.            *)
  (* Tout texte nu entre éléments est un nœud texte flottant.        *)
  (* ^eot* et ^_* sont des éléments comme les autres : c'est le      *)
  (* parseur qui interrompt la lecture à leur rencontre, pas la       *)
  (* grammaire qui interdit ce qui les suit.                          *)

node
  = element | root-control-code | text-node ;


(* ═══════════════════════════════════════════════════════════ *)
(*  ÉLÉMENTS — dispatcher principal                            *)
(* ═══════════════════════════════════════════════════════════ *)

element
  = paired-element
  | quoted-element
  | empty-element
  | verbatim-element
  | control-element
  | escape-element ;
  (* Note : control-element autorise ^_* et ^gs* dans un élément. *)
  (* ^eot* est exclu — il appartient uniquement à root-control-code. *)


(* ═══════════════════════════════════════════════════════════ *)
(*  FORME 1 & 2 — paired : ^tag attr=''val'': ... _tag:       *)
(* ═══════════════════════════════════════════════════════════ *)

paired-element
  = open-tag , content , close-tag ;

open-tag
  = "^" , element-name , { attribute } , ":" ;
  (* Zéro attribut  : "^titre:"                    *)
  (* Un attribut    : "^doc markup=''3.0'':"        *)
  (* Plusieurs      : "^img src=''x'' alt=''y'':"   *)

close-tag
  = "_" , element-name , ":" ;
  (* Doit correspondre exactement au nom de l'open-tag associé. *)

content
  = { node | happy-ending } ;
  (* happy-ending termine la portée courante si rencontré. *)


(* ═══════════════════════════════════════════════════════════ *)
(*  FORME QUOTÉE — ^tag''contenu''                            *)
(*  Sucre syntaxique pour contenu inline texte pur            *)
(* ═══════════════════════════════════════════════════════════ *)

quoted-element
  = "^" , element-name , { attribute } , wriml-quote-mark , inline-content , wriml-quote-mark ;
  (* Restriction : inline-content ne peut pas contenir de sous-éléments. *)
  (* Usage recommandé : contenu court, balises inline (^em, ^fort, etc.) *)
  (* Exemple valide   : ^em''mot en italique''                            *)
  (* Exemple invalide : ^em''texte ^fort''gras''''                        *)

inline-content
  = { inline-character } ;
  (* Tout caractère sauf wriml-quote-mark et "^".         *)
  (* "^" est toujours actif : interdit dans inline-content *)
  (* sans échappement via ^cfx*.                           *)

inline-character
  = text-character - wriml-quote-mark - "^" ;


(* ═══════════════════════════════════════════════════════════ *)
(*  FORME 3 & 4 — auto-fermant : ^tag attr=''val''*           *)
(* ═══════════════════════════════════════════════════════════ *)

empty-element
  = "^" , element-name , { attribute } , "*" ;
  (* Exemple : ^br*   ^img src=''logo.png'' alt=''Logo''* *)


(* ═══════════════════════════════════════════════════════════ *)
(*  ÉLÉMENTS VERBATIM                                         *)
(*  Le contenu n'est PAS parsé — tout caractère est accepté   *)
(* ═══════════════════════════════════════════════════════════ *)

verbatim-element
  = code-element | comment-element ;

(* ^code : bloc de code — environnement strictement verbatim *)
code-element
  = "^code" , { attribute } , ":" , { character } , "_code:" ;

(* ^com / ^cmt / ^rem / ^- / ^# / ^comment : commentaire verbatim *)
comment-element
  = "^" , comment-name , { attribute } , ":" , { character } , "_" , comment-name , ":" ;
  (* Fermeture : _com: _cmt: _rem: _-: _#: _comment:           *)
  (* Utilise "_name:" comme tout élément WRIML — pas d'exception*)

comment-name
  = "com" | "cmt" | "rem" | "comment" | "#" | "-" ;
  (* "-" ajouté : ^-:commentaire court_-:                       *)


(* ═══════════════════════════════════════════════════════════ *)
(*  CONTRÔLE — deux niveaux distincts                         *)
(* ═══════════════════════════════════════════════════════════ *)

(* Contrôles valides uniquement à la racine du document.       *)
(* Intégrés dans node, jamais dans element.                    *)
root-control-code
  = happy-ending           (* ^_* à la racine : termine le document  *)
  | end-of-transmission ;  (* ^eot* : termine le document            *)
  (* ^gs* absent : un Group Separator à la racine n'a           *)
  (* aucune sémantique — interdit formellement dès v3.0.        *)

(* Contrôles valides à l'intérieur d'un élément.               *)
control-element
  = happy-ending     (* ^_* : ferme la portée courante             *)
  | group-separator ;  (* ^gs* : sépare deux occurrences adjacentes*)
  (* ^eot* absent : interdit dans un élément dès v3.0.          *)
  (* Un parseur DOIT lever une ERREUR si ^eot* est rencontré    *)
  (* à l'intérieur d'un élément.                                *)

(* ^_* : comportement selon le contexte                        *)
(*   Dans control-element : ferme l'élément, ignore le reste.  *)
(*   Dans root-control-code : termine le document.             *)
happy-ending
  = "^_*" ;

(* ^eot* : fin de document — racine uniquement.                *)
(* ERREUR formelle si rencontré dans un élément.               *)
end-of-transmission
  = "^eot*" ;

(* ^gs* : Group Separator — intérieur d'un élément uniquement. *)
(* ERREUR formelle si rencontré à la racine.                   *)
group-separator
  = "^gs*" ;


(* ═══════════════════════════════════════════════════════════ *)
(*  ÉLÉMENTS D'ÉCHAPPEMENT                                    *)
(*  Philosophie : tout est élément, même l'échappement.       *)
(* ═══════════════════════════════════════════════════════════ *)

escape-element
  = circumflex-char
  | underscore-char
  | dash-char
  | char-element ;

(* ^cfx* : insère ^ littéral — OBLIGATOIRE pour tout ^ dans le texte *)
circumflex-char
  = "^cfx*" ;

(* ^us* / ^underscore* : insère _ littéral *)
underscore-char
  = "^us*" | "^underscore*" ;

(* ^dash* : insère - littéral *)
dash-char
  = "^dash*" ;

(* ^chr / ^char : insère tout caractère Unicode par point de code *)
char-element
  = "^" , char-element-name , { attribute } , "*" ;

char-element-name
  = "chr" | "char" ;

(* Exemple : ^chr code=''94''*  → ^         *)
(*           ^chr code=''8212''* → — (em dash) *)


(* ═══════════════════════════════════════════════════════════ *)
(*  ÉLÉMENTS PRÉDÉFINIS                                       *)
(* ═══════════════════════════════════════════════════════════ *)

(* Paragraphe : toujours paired *)
paragraph-element
  = "^" , paragraph-name , { attribute } , ":" , content , "_" , paragraph-name , ":" ;

paragraph-name
  = "p" | "par" | "paragraph" ;
  (* Les trois formes sont des alias équivalents. *)


(* ═══════════════════════════════════════════════════════════ *)
(*  NOMS DE BALISES ET NAMESPACES                             *)
(* ═══════════════════════════════════════════════════════════ *)

element-name
  = reserved-name | user-name ;

(* Noms réservés : définis par la spécification WRIML.         *)
(* Syntaxiquement valides, sémantiquement définis.             *)
(* INTERDITS à la redéfinition par l'utilisateur.              *)
reserved-name
  = "_" | "-" | "#"
  | "doc" | "document"
  | "import"                    (* permet d'importer des ressources externes *)
  | "tag-decl"
  | "com" | "cmt" | "rem" | "comment"
  | "cfx" | "us" | "underscore" | "dash"
  | "chr" | "char"
  | "gs" | "eot"
  | "p" | "par" | "paragraph"
  | "code" ;

(* Noms libres : définis par l'utilisateur.                    *)
(* Peuvent être préfixés d'un namespace.                       *)
user-name
  = [ namespace "." ] base-name ;
  (* Sans namespace : ^titre:                                   *)
  (* Avec namespace : ^doc.titre:                               *)
  (* Recommandation : max 2 segments (namespace + base-name)    *)
  (* Autorisé mais déconseillé : ^org.monsite.titre:            *)

namespace
  = base-name , { "." , base-name } ;

base-name
  = letter , { name-char } ;
  (* Un nom libre commence toujours par une lettre.             *)
  (* Les noms réservés "_" "-" "#" échappent à cette règle      *)
  (* car ils sont traités comme reserved-name, hors base-name.  *)

name-char
  = letter | digit | safe-symbol-l1 | safe-symbol-l2 ;

safe-symbol-l1
  = "-" | "_" ;
  (* Couche 1 — usage ordinaire recommandé.                     *)
  (* Suffisant pour 99% des noms de balises.                    *)
  (* Exemples : ^mon-tag: ^nom_long:                            *)

safe-symbol-l2
  = "@" | "$" | "£" | "~" | "`" | "+" | "&" | "#" | "|" ;
  (* Couche 2 — usage avancé, fortement déconseillé             *)
  (* en dehors du développement de sous-langages WRIML.         *)
  (* Exclus définitivement : "/" "\" et les caractères actifs   *)
  (* WRIML ("^" "_" ":") et le digraphe "''".                   *)


(* ═══════════════════════════════════════════════════════════ *)
(*  ATTRIBUTS                                                  *)
(* ═══════════════════════════════════════════════════════════ *)

attribute
  = attr-separator , attr-name , "=" , wriml-quote-mark , attr-value , wriml-quote-mark ;

attr-separator
  = ( space | line-break ) , { space } ;
  (* Au moins un espace ou un retour à la ligne.                *)
  (* Suivi de 0 ou N espaces supplémentaires (alignement).      *)
  (* \n\n formellement interdit : le deuxième \n ne peut pas    *)
  (* suivre immédiatement le premier dans cette règle.          *)
  (* Exemple sur plusieurs lignes :                             *)
  (*   ^doc markup=''3.0''                                      *)
  (*        version=''1.0''                                     *)
  (*        date=''2026-05-01'':                                *)

attr-name
  = system-keyword | normal-attr-name ;

(* Attribut ordinaire : pas de point dans le nom *)
normal-attr-name
  = letter , { letter | digit | "-" | "_" } ;
  (* Le point est INTERDIT dans un nom d'attribut ordinaire.    *)

(* Mot-clé système : préfixe réservé suivi d'un point          *)
(* Le point fait partie intégrante du token — pas un opérateur *)
system-keyword
  = system-prefix , "." , letter , { letter | digit | "-" | "_" } ;

system-prefix
  = "wriml"              (* réservé à la spécification officielle WRIML *)
  | third-party-prefix ;

third-party-prefix
  = letter , { letter | digit } ;
  (* Convention : préfixe court, non ambigu, ne commençant pas par "wriml". *)
  (* Exemples : whtml, wsvg, wdata                                           *)

attr-value
  = { graphic-character } ;
  (* Tout caractère graphique sauf wriml-quote-mark.            *)


(* ═══════════════════════════════════════════════════════════ *)
(*  TEXTE NU                                                  *)
(* ═══════════════════════════════════════════════════════════ *)

text-node
  = text-segment ;
  (* Un text-node est un nœud texte flottant dans l'arbre.      *)
  (* Il n'est PAS implicitement enveloppé dans ^p:              *)
  (* NOTE : cette grammaire ne formalise pas la séparation      *)
  (* paragraphique. \n\n est du texte comme les autres          *)
  (* caractères du point de vue de la grammaire v3.0.           *)
  (* La séparation de paragraphes par \n\n est une convention   *)
  (* de rendu, non une règle syntaxique.                        *)
  (* Une formalisation complète est réservée à v3.1+.           *)

text-segment
  = text-character , { text-character } ;

text-character
  = graphic-character | carriage-control-character ;
  (* "^" est TOUJOURS actif : interdit comme caractère texte.   *)
  (* Un "^" non suivi d'un element-name valide = ERREUR.        *)
  (* "_" seul, non suivi de element-name + ":" = texte libre.   *)
  (* \n\n : voir note d'implémentation sur les frontières.      *)


(* ═══════════════════════════════════════════════════════════ *)
(*  TERMINAUX UNICODE                                         *)
(* ═══════════════════════════════════════════════════════════ *)

wriml-quote-mark
  = "''" ;
  (* Digraphe atomique : deux apostrophes U+0027 consécutives.  *)
  (* Toujours traité comme un seul token délimiteur.            *)
  (* Une apostrophe simple ' est toujours du texte libre.       *)

character
  = [#x1-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF] ;
  (* Tout caractère Unicode hors blocs surrogates et #xFFFE/#xFFFF. *)

graphic-character
  = [#x20-#x0026]                (* espace à & — exclut ' U+0027        *)
  | [#x0028-#xD7FF]              (* ( à fin BMP hors surrogates          *)
  | [#xE000-#xFFFD]
  | [#x10000-#x10FFFF] ;
  (* Exclut les caractères de contrôle (#x0-#x1F sauf gérés ci-dessous) *)
  (* et l'apostrophe U+0027 pour éviter l'ambiguïté avec wriml-quote-mark*)

carriage-control-character
  = #x08                         (* BS  Backspace          *)
  | #x09                         (* HT  Horizontal Tab     *)
  | #x0A                         (* LF  Line Feed          *)
  | #x0D ;                       (* CR  Carriage Return    *)

line-break
  = #x0A | ( #x0D , #x0A ) | #x0D ;
  (* LF | CRLF | CR — les trois conventions de fin de ligne.   *)

space
  = #x20 | #x09 ;
  (* Espace ordinaire ou tabulation horizontale.                *)

letter
  = [#x41-#x5A] | [#x61-#x7A] ;
  (* A-Z et a-z uniquement. Lettres Unicode étendues : v3.1+.  *)

digit
  = [#x30-#x39] ;
  (* 0-9. *)
```

---

## Notes d'implémentation

### `^` — caractère toujours actif
`^` déclenche **toujours** la reconnaissance d'un élément. Le parseur tente de lire un `element-name` valide après `^`. Si la séquence ne correspond à aucune règle d'élément, c'est une **erreur de syntaxe** — jamais un caractère texte silencieux. Pour insérer `^` littéral : `^cfx*`, sans exception.

### `_` — contexte-dépendant
`_` est interprété comme début de `close-tag` **seulement** s'il est immédiatement suivi d'un `element-name` valide et de `:`. Sinon, c'est un caractère texte ordinaire. Le parseur doit faire un lookahead minimal pour distinguer les deux cas.

### `''` — digraphe atomique
Deux apostrophes U+0027 consécutives forment un seul token. Le parseur les reconnaît comme `wriml-quote-mark` en priorité, avant toute autre interprétation. Une apostrophe simple `'` est toujours du texte libre, inerte dans tous les contextes.

### Symboles dans les noms de balises — deux couches
Les symboles autorisés dans `name-char` suivent l'architecture en deux couches de WRIML :

**Couche 1** — `safe-symbol-l1` : `"-"` et `"_"` uniquement. Suffisants pour tous les usages ordinaires. C'est ce qu'un utilisateur WRIML doit connaître.

**Couche 2** — `safe-symbol-l2` : symboles étendus pour développeurs de sous-langages. Syntaxiquement autorisés, fortement déconseillés en usage courant car potentiellement source de confusion pour les lecteurs et les outils tiers.

Symboles exclus définitivement (conflits de parsing réels) :

| Symbole | Raison |
|---|---|
| `/` `\` | Opérateurs d'échappement et chemins de fichiers |
| `^` `_` `:` `*` | Caractères actifs WRIML |
| `''` | Digraphe délimiteur WRIML |

**Exception** : `"#"` est autorisé en Couche 1 uniquement dans `comment-name` — règle isolée et explicitement documentée, non propagée à `name-char` général.

### Forme quotée — restriction d'imbrication
`quoted-element` utilise `inline-content` qui **interdit `^`**. Un parseur rencontrant `^` à l'intérieur d'un `inline-content` doit lever une erreur de syntaxe, pas tenter de parser un sous-élément. Cette restriction est intentionnelle : la forme quotée est réservée au texte pur.

### Portée de `happy-ending`
Le parseur maintient une pile de portées (`scope-stack`). `^_*` appartient à la fois à `root-control-code` et à `control-element` — son comportement dépend du contexte : dans un élément, il dépile la portée courante et ignore tous les tokens suivants jusqu'à la fermeture parente attendue ; à la racine (pile vide), il termine le document, équivalent à `^eot*`.

### `end-of-transmission`
`^eot*` appartient uniquement à `root-control-code` — il est formellement interdit à l'intérieur d'un élément dès v3.0. Un parseur **doit** lever une **erreur** s'il rencontre `^eot*` dans un élément. Ce choix est intentionnel : pas de période de grâce, les utilisateurs apprennent la règle dès le départ. En v3.1, `root-control-code` sera migré directement dans `node` et retiré de `element` pour nettoyer l'architecture.

### `group-separator`
`^gs*` appartient uniquement à `control-element` — il est formellement interdit à la racine dès v3.0. Un `^gs*` à la racine n'a aucune sémantique (il n'y a aucun groupe à séparer) — un parseur **doit** lever une **erreur**.

### Verbatim
Dans `code-element` et `comment-element`, le contenu est `{ character }` — le parseur lit tout caractère Unicode valide sans tenter de reconnaître `^`, `_` ou `''`. La seule séquence qui met fin au verbatim est la fermeture correspondante (`_code:`, `_com:`, `_-:`, etc.). Le parseur doit implémenter un scan de séquence terminale, pas un parsing récursif, à l'intérieur d'un bloc verbatim. Les formes quotées pour `code` et `comment` ont été supprimées — ces environnements sont par nature multi-lignes et incompatibles avec l'esprit inline des quoted-elements.

### Noms réservés — `reserved-name`
Tout nom figurant dans `reserved-name` est **interdit à la redéfinition** par l'utilisateur. Un parseur strict doit lever une erreur si un `user-name` correspond à un `reserved-name`. La liste est exhaustive pour v3.0 — des noms supplémentaires pourront être réservés dans les versions v3.x.

### `text-node` et séparation paragraphique
La grammaire v3.0 ne formalise pas la séparation de paragraphes. `\n\n` est syntaxiquement du texte ordinaire — `text-segment` peut le traverser sans s'arrêter. La séparation de paragraphes par `\n\n` est une **convention de rendu** que les outils peuvent implémenter librement, pas une règle syntaxique imposée par la grammaire. Une formalisation complète avec `paragraph` et `paragraph-break` est réservée à v3.1+.

### Namespaces
Le point `.` dans `user-name` est un séparateur de namespace. Il est **interdit** dans `normal-attr-name`. Seuls les `system-keyword` utilisent le point dans un nom d'attribut, et il y fait partie d'un token réservé atomique — pas un mécanisme général étendu aux attributs ordinaires.

### Roadmap architecture contrôle — v3.1
En v3.1, `control-element` sera retiré d'`element` et `root-control-code` sera renommé `control-code` et intégré directement dans `node` :

```ebnf
node    = element | control-code | text-node ;
element = paired-element | quoted-element | empty-element
        | verbatim-element | escape-element ;
        (* control-element supprimé *)

control-code = happy-ending | end-of-transmission | group-separator ;
        (* GS reste interdit à la racine — règle sémantique dans les notes *)
```

Cette migration est **non-breaking** : tout document v3.0 valide reste valide en v3.1, sauf usage de `^eot*` dans un élément ou `^gs*` à la racine — déjà des erreurs en v3.0.

---

*Grammaire WRIML 3.0 fusionnée & corrigée · MIT © https://github.com/dbjoshua*
