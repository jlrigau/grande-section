# -*- coding: utf-8 -*-
"""Contrôle les cartes-corpus avant publication.

Quatre vérifications :

- **la couverture** : chaque nom des trois corpus de `01-projet-annuel.md`
  doit avoir une carte, ou être déclaré dans NON_ILLUSTRES (les verbes et les
  adjectifs). Un mot ajouté à un corpus sans carte fait échouer le contrôle
  au lieu de passer inaperçu — c'est le même filet que `couverture.py` pour
  le programme ;
- **les fichiers** : l'image de chaque carte doit exister là où le manifeste
  la désigne ;
- **les crédits de la banque** : source, licence et auteur renseignés. Les
  règles de licence sont celles du skill `fiches-illustrations` — Mulberry
  d'abord, ARASAAC accepté à défaut ;
- **les crédits** : une image moissonnée sans jeu ni licence ne peut pas être
  publiée ;
- **les doublons** : deux cartes ne peuvent pas porter les mêmes octets.
  Openclipart rend silencieusement son propre logo — des ciseaux blancs sur
  fond vert — pour une partie des identifiants, avec des crédits parfaitement
  corrects : deux cartes s'étaient retrouvées avec cette image-là. Le seul
  signe visible était que les deux fichiers pesaient exactement pareil.

Usage : python3 scripts/verifier-cartes-corpus.py
Sortie : code 1 s'il reste quelque chose à corriger.
"""
import json
import hashlib
import os
import re
import sys
import unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ICI, "..", "site")
BASE = os.path.join(SITE, "cartes-corpus")

ns = {}
exec(compile(open(os.path.join(ICI, "corpus-manifest.py"), encoding="utf-8").read(),
             "corpus-manifest.py", "exec"), ns)
entrees, CARTES, GROUPES = ns["entrees"], ns["CARTES"], ns["GROUPES"]
NON_ILLUSTRES = ns["NON_ILLUSTRES"]

credits_fiches = json.load(open(os.path.join(SITE, "fiches", "img", "credits.json"),
                                encoding="utf-8"))

ennuis = []
# md5 → slugs : deux cartes qui partagent leurs octets sont un accident
empreintes = {}


def normalise(mot):
    """« l'écureuil » et « écureuil » sont le même mot ; les corpus écrivent
    l'article, pas toujours le même."""
    m = mot.strip().lower().replace("’", "'")
    m = re.sub(r"^(le |la |les |l'|un |une )", "", m)
    return "".join(c for c in unicodedata.normalize("NFD", m)
                   if unicodedata.category(c) != "Mn")


# ── 1. Couverture des corpus ──────────────────────────────────────────────
projet = open(os.path.join(ICI, "..", "01-projet-annuel.md"), encoding="utf-8").read()
section = projet.split("## 3. Corpus de vocabulaire")[1].split("## 4.")[0]
mots_corpus = {}
for ligne in section.split("\n"):
    m = re.match(r"\| P(\d) \w+ \|(.*)\|\s*$", ligne)
    if m:
        mots_corpus[int(m.group(1))] = [w.strip() for c in m.group(2).split("|")
                                        for w in c.split(",") if w.strip()]
if len(mots_corpus) != 5:
    ennuis.append("le tableau des corpus de 01-projet-annuel.md n'a pas 5 lignes")

for p, mots in sorted(mots_corpus.items()):
    cartes = {normalise(nom) for _, _, _, nom, _ in entrees(p)}
    declares = {normalise(m) for m in NON_ILLUSTRES.get(p, ())}
    for mot in mots:
        if normalise(mot) not in cartes and normalise(mot) not in declares:
            ennuis.append("P%d  « %s » : ni carte ni mot déclaré non illustrable" % (p, mot))
    for mot in declares - {normalise(m) for m in mots}:
        ennuis.append("P%d  « %s » déclaré non illustrable mais absent du corpus" % (p, mot))

# ── 2. Les images : deux provenances, et la banque partagée ──────────────
# Pas de banque propre aux cartes-corpus : les pictogrammes viennent de
# site/fiches/img/, alimentée par scripts/chercher-pictos.py (skill
# fiches-illustrations). Un mot dont le slug n'y est pas encore est signalé
# comme « à installer », avec la commande qui le fait.
a_installer, vus = [], set()
for p, groupe, slug, nom, source in entrees():
    if slug in vus:
        continue
    vus.add(slug)
    genre, valeur = source
    if genre == "imagier":
        chemin = os.path.join(SITE, "imagier", "img", valeur + ".jpg")
        if not os.path.exists(chemin):
            ennuis.append("%-16s photographie d'imagier absente : %s" % (slug, valeur))
        continue
    credit = credits_fiches.get(valeur)
    if not credit:
        # peut-être une référence par nom de fichier plutôt que par slug
        credit = credits_fiches.get(os.path.splitext(valeur)[0])
    if not credit:
        a_installer.append(slug)
        continue
    for champ in ("source", "licence", "auteur"):
        if not credit.get(champ):
            ennuis.append("%-16s crédit incomplet dans la banque (%s)" % (slug, champ))
    chemin = os.path.join(SITE, "fiches", "img", credit["fichier"])
    if not os.path.exists(chemin):
        ennuis.append("%-16s image absente : %s" % (slug, credit["fichier"]))
    else:
        empreintes.setdefault(hashlib.md5(open(chemin, "rb").read()).hexdigest(),
                              []).append(slug)

for slugs in empreintes.values():
    if len(slugs) > 1:
        ennuis.append("images identiques au bit près : %s" % ", ".join(sorted(slugs)))

# ── 3. Les pages sont-elles à jour ? ──────────────────────────────────────
for p in sorted(CARTES):
    page = os.path.join(BASE, "periode-%d.html" % p)
    if not os.path.exists(page):
        ennuis.append("periode-%d.html absent — lancer generer-cartes-corpus.py" % p)
        continue
    html = open(page, encoding="utf-8").read()
    attendu = sum(1 for _ in entrees(p))
    trouve = html.count('<div class="carte">')
    if trouve != attendu * 2:          # cartes de contrôle + cartes-images
        ennuis.append("periode-%d.html : %d cartes pour %d mots — page à régénérer"
                      % (p, trouve, attendu))

if a_installer:
    print("%d mot·s dont l'image reste à installer dans la banque partagée :"
          % len(a_installer))
    print("  " + ", ".join(sorted(a_installer)))
    print("  → python3 scripts/chercher-pictos.py chercher <slug> \"<mots anglais>\"")
    print("  → puis  installer <slug> mulberry:<nom>  (skill fiches-illustrations)")
    ennuis.append("%d image·s manquent encore" % len(a_installer))

for e in ennuis:
    print("✗ " + e)
print("%d cartes contrôlées sur 5 cahiers, %d anomalie(s)" % (len(vus), len(ennuis)))
sys.exit(1 if ennuis else 0)
