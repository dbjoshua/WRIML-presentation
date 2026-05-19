"""
tests/test_parser.py — Tests syntaxiques du parseur WRIML v3

Corpus de cas valides et invalides conformes au brief (§ 7).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from wriml import parse
from wriml.ast import DocumentNode, ElementNode, TextNode, ControlNode
from wriml.errors import LexerError, ParseError, WRIMLError


# ═══════════════════════════════════════════════════════════════════════════
#  CAS VALIDES
# ═══════════════════════════════════════════════════════════════════════════

class TestDocumentBasique:

    def test_document_vide(self):
        doc = parse("")
        assert isinstance(doc, DocumentNode)
        assert doc.children == []

    def test_texte_nu(self):
        doc = parse("Bonjour le monde")
        assert len(doc.children) == 1
        assert isinstance(doc.children[0], TextNode)
        assert doc.children[0].text == "Bonjour le monde"

    def test_element_simple_paired(self):
        doc = parse("^section:_section:")
        assert len(doc.children) == 1
        el = doc.children[0]
        assert isinstance(el, ElementNode)
        assert el.name == "section"
        assert el.kind == "paired"

    def test_element_avec_texte(self):
        doc = parse("^p:Bonjour_p:")
        el = doc.children[0]
        assert el.name == "p"
        assert len(el.children) == 1
        assert isinstance(el.children[0], TextNode)
        assert el.children[0].text == "Bonjour"

    def test_multi_racine(self):
        doc = parse("^a:_a:^b:_b:")
        assert len(doc.children) == 2
        assert doc.children[0].name == "a"
        assert doc.children[1].name == "b"


class TestAttributs:

    def test_attribut_simple(self):
        doc = parse("^section titre=''Introduction'':_section:")
        el = doc.children[0]
        assert el.attributes == {"titre": "Introduction"}

    def test_attributs_multiples(self):
        doc = parse("^doc markup=''3.0'' date=''2026-05-01'':_doc:")
        el = doc.children[0]
        assert el.attributes["markup"] == "3.0"
        assert el.attributes["date"] == "2026-05-01"

    def test_attribut_valeur_vide(self):
        doc = parse("^br alt='':_br:")
        el = doc.children[0]
        assert el.attributes["alt"] == ""

    def test_attribut_multiligne(self):
        src = "^doc markup=''3.0''\n     date=''2026-05-01'':_doc:"
        doc = parse(src)
        el = doc.children[0]
        assert el.attributes["markup"] == "3.0"
        assert el.attributes["date"] == "2026-05-01"


class TestImbrication:

    def test_imbrication_simple(self):
        src = "^section:^p:Bonjour_p:_section:"
        doc = parse(src)
        section = doc.children[0]
        assert section.name == "section"
        p = section.children[0]
        assert p.name == "p"
        assert p.children[0].text == "Bonjour"

    def test_imbrication_profonde(self):
        src = "^a:^b:^c:texte_c:_b:_a:"
        doc = parse(src)
        a = doc.children[0]
        b = a.children[0]
        c = b.children[0]
        assert c.name == "c"
        assert c.children[0].text == "texte"

    def test_element_vide_inside(self):
        src = "^p:début^br*fin_p:"
        doc = parse(src)
        p = doc.children[0]
        assert p.children[0].text == "début"
        assert p.children[1].name == "br"
        assert p.children[1].kind == "empty"
        assert p.children[2].text == "fin"


class TestFormesCourtes:

    def test_auto_fermant(self):
        doc = parse("^br*")
        el = doc.children[0]
        assert el.name == "br"
        assert el.kind == "empty"
        assert el.children == []

    def test_auto_fermant_avec_attributs(self):
        doc = parse("^img src=''logo.png'' alt=''Logo''*")
        el = doc.children[0]
        assert el.name == "img"
        assert el.attributes["src"] == "logo.png"
        assert el.attributes["alt"] == "Logo"

    def test_forme_quotee(self):
        doc = parse("^em''mot en italique''")
        el = doc.children[0]
        assert el.name == "em"
        assert el.kind == "quoted"
        assert el.children[0].text == "mot en italique"

    def test_forme_quotee_vide(self):
        doc = parse("^gr''''")
        el = doc.children[0]
        assert el.kind == "quoted"
        assert el.children[0].text == ""


class TestControles:

    def test_happy_ending_racine(self):
        doc = parse("^a:_a:^_*texte ignoré")
        # ^_* à la racine termine le document — le texte après est ignoré
        assert len(doc.children) == 1

    def test_happy_ending_dans_element(self):
        src = "^p:texte^_*"
        doc = parse(src)
        p = doc.children[0]
        assert p.children[0].text == "texte"

    def test_eot_termine_document(self):
        doc = parse("^a:_a:^eot*texte ignoré")
        assert len(doc.children) == 1

    def test_gs_dans_element(self):
        src = "^gl:^gr''foc''^gs*^gr''3''_gl:"
        doc = parse(src)
        gl = doc.children[0]
        assert any(isinstance(c, ElementNode) and c.name == "gr" for c in gl.children)
        assert gl.group_separators  # au moins une position GS enregistrée


class TestVerbatim:

    def test_bloc_code(self):
        src = "^code:print(''hello'')_code:"
        doc = parse(src)
        el = doc.children[0]
        assert el.name == "code"
        assert el.kind == "verbatim"
        assert "print" in el.verbatim_content

    def test_bloc_commentaire_com(self):
        src = "^com:Ceci est un commentaire_com:"
        doc = parse(src)
        el = doc.children[0]
        assert el.kind == "verbatim"
        assert "commentaire" in el.verbatim_content

    def test_verbatim_contenu_non_parse(self):
        src = "^code:^section:non parsé_section:_code:"
        doc = parse(src)
        el = doc.children[0]
        assert el.kind == "verbatim"
        assert "^section:" in el.verbatim_content


class TestEchappements:

    def test_cfx(self):
        doc = parse("^cfx*")
        el = doc.children[0]
        assert el.name == "cfx"
        assert el.kind == "escape"

    def test_underscore(self):
        doc = parse("^us*")
        el = doc.children[0]
        assert el.name == "us"

    def test_dash(self):
        doc = parse("^dash*")
        el = doc.children[0]
        assert el.name == "dash"

    def test_chr_avec_attribut(self):
        doc = parse("^chr code=''94''*")
        el = doc.children[0]
        assert el.name == "chr"
        assert el.attributes["code"] == "94"


class TestNamespace:

    def test_namespace_simple(self):
        doc = parse("^ling.titre:Analyse_ling.titre:")
        el = doc.children[0]
        assert el.name == "ling.titre"

    def test_namespace_deep(self):
        doc = parse("^org.wriml.test:contenu_org.wriml.test:")
        el = doc.children[0]
        assert el.name == "org.wriml.test"


class TestExportJSON:

    def test_to_json_retourne_string(self):
        doc = parse("^p:texte_p:")
        j = doc.to_json()
        import json
        d = json.loads(j)
        assert d["type"] == "document"
        assert d["children"][0]["name"] == "p"

    def test_to_json_attributs(self):
        doc = parse("^doc markup=''3.0'':_doc:")
        import json
        d = json.loads(doc.to_json())
        el = d["children"][0]
        assert el["attributes"]["markup"] == "3.0"


# ═══════════════════════════════════════════════════════════════════════════
#  CAS INVALIDES — le parseur DOIT lever des erreurs
# ═══════════════════════════════════════════════════════════════════════════

class TestErreurs:

    def test_balise_non_fermee(self):
        with pytest.raises(WRIMLError) as exc_info:
            parse("^section:")
        assert "non fermée" in str(exc_info.value) or "fin de fichier" in str(exc_info.value).lower()

    def test_fermeture_incorrecte(self):
        with pytest.raises(ParseError) as exc_info:
            parse("^section:^p:texte_section:")
        msg = str(exc_info.value)
        assert "section" in msg or "inattendue" in msg

    def test_fermeture_inattendue(self):
        with pytest.raises((ParseError, LexerError)):
            parse("_section:")  # fermeture sans ouverture — OK si ignoré ou erreur

    def test_eot_dans_element(self):
        with pytest.raises(ParseError) as exc_info:
            parse("^p:^eot*_p:")
        assert "interdit" in str(exc_info.value)

    def test_gs_a_la_racine(self):
        with pytest.raises(ParseError) as exc_info:
            parse("^gs*")
        assert "racine" in str(exc_info.value)

    def test_attribut_sans_valeur(self):
        with pytest.raises(WRIMLError):
            parse("^p titre:_p:")

    def test_circumflex_seul(self):
        with pytest.raises(WRIMLError):
            parse("^")

    def test_code_non_ferme(self):
        with pytest.raises(WRIMLError):
            parse("^code:contenu sans fermeture")


# ═══════════════════════════════════════════════════════════════════════════
#  EXEMPLE DU SITE OFFICIEL
# ═══════════════════════════════════════════════════════════════════════════

class TestExempleOfficiel:

    def test_corpus_wriml(self):
        src = (
            "^doc markup=''3.0'' date=''2026-05-02'':\n"
            "  ^titre:Analyse morphologique_titre:\n"
            "  ^data:\n"
            "    ^mb:tralE jE O fa-li O_mb:\n"
            "    ^gl:habit ^gr''foc'' ^gr''3''^gr''sg''\n"
            "      prendre-^gr''pas''.^gr''perf''_gl:\n"
            "    ^ft:C'est un habit qu'il a pris_ft:\n"
            "  _data:\n"
            "_doc:"
        )
        doc = parse(src)
        assert doc.children[0].name == "doc"
        doc_el = doc.children[0]
        assert doc_el.attributes["markup"] == "3.0"

    def test_multiracine(self):
        src = "^a:_a:^b:_b:^c:_c:"
        doc = parse(src)
        assert len(doc.children) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
