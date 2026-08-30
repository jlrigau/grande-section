# -*- coding: utf-8 -*-
"""Contrôle les photographies de l'imagier avant publication.

Trois vérifications, chacune née d'une erreur passée inaperçue :

- **l'espèce** : le taxon de l'observation créditée doit être celui du
  manifeste. La recherche par nom vernaculaire avait fait entrer un blaireau
  d'Amérique pour « le blaireau » et un rhebok d'Afrique du Sud pour « le
  chevreuil » ;
- **les crédits** : une photographie sans auteur ni licence ne peut pas être
  publiée ;
- **le cadrage** : une image qui ne remplit pas la carte laisse une bande
  blanche, visible de loin sur le matériel imprimé ;
- **les chiffres annoncés** : le site et les documents disent combien
  d'espèces contient chaque cahier. Quand l'imagier a doublé, les pages
  générées ont suivi — elles comptent le manifeste — mais le site est resté
  sur les anciens chiffres, et l'enseignante a lu « 9 espèces » devant un
  cahier qui en contenait trente-six.

Usage : python3 scripts/verifier-imagier.py
Sortie : code 1 s'il reste quelque chose à corriger.
"""
import json, os, re, ssl, sys, time, urllib.parse, urllib.request
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ICI, "..", "site", "imagier", "img")
ns = {}
exec(compile(open(os.path.join(ICI, "imagier-manifest.py"), encoding="utf-8").read(),
             "imagier-manifest.py", "exec"), ns)
ATTENDUES = {slug for _, _, slug, _, _ in ns["entrees"]()}

# renommages acceptés : iNaturalist a raison, le manifeste garde le nom d'usage
SYNONYMES = {
    "Ammophila arenaria": "Calamagrostis arenaria",
    "Anemone nemorosa": "Anemonoides nemorosa",
    "Ichthyosaura alpestris": "Mesotriton alpestris",
    "Halimione portulacoides": "Atriplex portulacoides",
}


def normalise(nom):
    """« Platanus x hispanica » et « Platanus × hispanica » sont le même
    hybride : le manifeste s'écrit au clavier, iNaturalist en typographie."""
    return nom.replace("\u00d7", "x").replace(" x ", " x ").strip()

cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
op = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent", "GS-imagier/1.0 (verification)")]

credits = json.load(open(os.path.join(IMG, "credits.json"), encoding="utf-8"))
ennuis = []

manquantes = sorted(ATTENDUES - set(credits))
for slug in manquantes:
    ennuis.append("%-24s absente des crédits" % slug)
for slug in sorted(ATTENDUES & set(credits)):
    v = credits[slug]
    if not v.get("auteur") or not v.get("licence"):
        ennuis.append("%-24s sans auteur ou sans licence" % slug)
    if not os.path.exists(os.path.join(IMG, v["fichier"])):
        ennuis.append("%-24s fichier absent" % slug)

# — le cadrage remplit-il la carte ? —
for slug in sorted(ATTENDUES & set(credits)):
    chemin = os.path.join(IMG, credits[slug]["fichier"])
    if not os.path.exists(chemin):
        continue
    im = Image.open(chemin).convert("RGB")
    l, h = im.size

    def blanche(boite):
        px = list(im.crop(boite).convert("RGB").getdata())
        return sum(1 for p in px if min(p) > 244) / len(px) > 0.97

    if (blanche((0, 0, l, 6)) and blanche((0, h - 6, l, h))) \
            or (blanche((0, 0, 6, h)) and blanche((l - 6, 0, l, h))):
        ennuis.append("%-24s bandes blanches : l'image ne remplit pas la carte" % slug)

# — l'espèce est-elle la bonne ? —
lots = [(s, credits[s]["taxon"], credits[s].get("observation", "").rstrip("/").split("/")[-1])
        for s in sorted(ATTENDUES & set(credits))]
lots = [t for t in lots if t[2].isdigit()]
for n in range(0, len(lots), 30):
    lot = lots[n:n + 30]
    url = "https://api.inaturalist.org/v1/observations/" + ",".join(o for _, _, o in lot)
    with op.open(url, timeout=45) as r:
        par_id = {str(o["id"]): o for o in json.load(r).get("results", [])}
    for slug, taxon, obs in lot:
        o = par_id.get(obs)
        if not o:
            ennuis.append("%-24s observation %s introuvable" % (slug, obs))
            continue
        nom = (o.get("taxon") or {}).get("name", "?")
        # le nom attendu, son renommage accepté, et les sous-espèces de l'un
        # comme de l'autre : « Mesotriton alpestris alpestris » reste le
        # triton alpestre du manifeste
        attendus = {a for a in (normalise(taxon), normalise(SYNONYMES.get(taxon, ""))) if a}
        vu = normalise(nom)
        if vu not in attendus and not any(vu.startswith(a + " ") for a in attendus):
            ennuis.append("%-24s espèce %s, attendu %s (%s)"
                          % (slug, nom, taxon, (o.get("place_guess") or "")[:30]))
    time.sleep(0.3)

# — les textes annoncent-ils le bon nombre d'espèces ? —
par_groupe = {}
for p_, groupe, slug, _, _ in ns["entrees"]():
    par_groupe.setdefault((p_, groupe), []).append(slug)
tailles = {len(v) for v in par_groupe.values()}
if len(tailles) == 1:
    n = tailles.pop()
    TEXTES = ("site/app.js", "README.md", "01-projet-annuel.md",
              "02-programmation-annuelle.md", "CLAUDE.md")
    motif = re.compile(r"(\d+)\s+(?:espèces de faune|animaux et)")
    for nom in TEXTES:
        chemin = os.path.join(ICI, "..", nom)
        if not os.path.exists(chemin):
            continue
        for ligne, texte in enumerate(open(chemin, encoding="utf-8"), 1):
            for trouve in motif.finditer(texte):
                if int(trouve.group(1)) != n:
                    ennuis.append("%-24s %s:%d annonce %s espèces, le manifeste en a %d"
                                  % ("chiffres annoncés", nom, ligne, trouve.group(1), n))
else:
    ennuis.append("%-24s les groupes n'ont pas tous la même taille : %s"
                  % ("manifeste", sorted(tailles)))

for e in ennuis:
    print("✗ " + e)
print("%d photographies contrôlées, %d anomalie(s)" % (len(ATTENDUES), len(ennuis)))
sys.exit(1 if ennuis else 0)
