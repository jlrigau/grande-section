# -*- coding: utf-8 -*-
"""Planches de candidats, pour choisir soi-même la photographie de chaque espèce.

Le tri automatique d'iNaturalist met en avant les photographies les plus
« aimées », qui sont souvent spectaculaires plutôt qu'illustratives (un ours
en train de manger des pissenlits, un bourgeon en gros plan…). Pour un
imagier, il faut au contraire une image où l'espèce est le sujet, entière et
reconnaissable. Ce script rassemble plusieurs candidates par espèce et les
assemble en une planche numérotée, à regarder avant de renseigner OVERRIDES
dans scripts/imagier-manifest.py.

Usage : python3 scripts/candidats-imagier.py [1-faune 1-flore 2-faune …]
        (sans argument : les dix planches)
Sortie : <DOSSIER>/candidats-p<N>-<groupe>.jpg  et  le JSON des identifiants
         (DOSSIER : variable d'environnement CANDIDATS_DIR, /tmp par défaut)
"""
import io, json, os, ssl, sys, time, urllib.error, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
ns = {}
exec(compile(open(os.path.join(ICI, "imagier-manifest.py"), encoding="utf-8").read(),
             "imagier-manifest.py", "exec"), ns)
ENTREES = list(ns["entrees"]())

DOSSIER = os.environ.get("CANDIDATS_DIR", "/tmp")
NB = int(os.environ.get("NB_CANDIDATS", "5"))
CELL, LEG = 330, 34
MIN_COTE = 1000
LICENCES = "cc0,cc-by,cc-by-sa"

cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "GS-imagier/1.0 (https://jlrigau.github.io/grande-section/)")]
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)


def ouvre(url, timeout=45):
    for attente in (0, 3, 8, 20):
        if attente:
            time.sleep(attente)
        try:
            return opener.open(url, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
    raise RuntimeError("serveur indisponible")


def candidates(taxon, recherche_seule=True):
    """Plusieurs photographies libres et imprimables, les plus appréciées
    d'abord. Le classement d'iNaturalist met en avant de belles images, pas
    forcément illustratives : c'est bien pourquoi on les regarde avant de
    choisir."""
    params = {"taxon_name": taxon, "photo_license": LICENCES, "photos": "true",
              "order_by": "votes", "per_page": "40"}
    if recherche_seule:
        params["quality_grade"] = "research"
    with ouvre("https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(params)) as r:
        d = json.load(r)
    out = []
    for obs in d.get("results", []):
        photo = (obs.get("photos") or [None])[0]   # la première photo est la mieux cadrée
        if not photo:
            continue
        dim = photo.get("original_dimensions") or {}
        l, h = dim.get("width", 0), dim.get("height", 0)
        if min(l, h) < MIN_COTE:
            continue
        out.append({"id": photo["id"], "vignette": photo["url"].replace("square", "medium"),
                    "accords": obs.get("num_identification_agreements", 0),
                    "paysage": l >= h})
    if not out and recherche_seule:
        return candidates(taxon, recherche_seule=False)
    # on garde l'ordre d'iNaturalist ; à qualité égale, une photo en
    # largeur remplit mieux la carte
    out.sort(key=lambda p: not p["paysage"])
    return out[:NB]


def planche(nom_fichier, especes):
    """especes : liste de (nom, taxon, [candidates])."""
    img = Image.new("RGB", (NB * CELL, len(especes) * (CELL + LEG)), "white")
    d = ImageDraw.Draw(img)
    for r, (nom, taxon, cands) in enumerate(especes):
        cy = r * (CELL + LEG)
        d.text((6, cy + CELL + 8), "%s  (%s)" % (nom, taxon), fill="black", font=F)
        for c, cand in enumerate(cands):
            cx = c * CELL
            try:
                with ouvre(cand["vignette"]) as rep:
                    v = Image.open(io.BytesIO(rep.read())).convert("RGB")
                v.thumbnail((CELL - 6, CELL - 6), Image.LANCZOS)
                img.paste(v, (cx + (CELL - v.width) // 2, cy + (CELL - v.height) // 2))
            except Exception as e:
                d.text((cx + 8, cy + 8), "échec", fill="red", font=F)
            d.rectangle([cx, cy, cx + CELL - 1, cy + CELL - 1], outline="#bbb")
            d.text((cx + 8, cy + 6), "%d" % (c + 1), fill="#c00", font=F)
    chemin = os.path.join(DOSSIER, nom_fichier)
    img.save(chemin, "JPEG", quality=86)
    return chemin


cibles = set(a.lower() for a in sys.argv[1:])
groupes = {}
for p, groupe, slug, nom, taxon in ENTREES:
    groupes.setdefault((p, groupe), []).append((slug, nom, taxon))

index = {}
for (p, groupe), especes in sorted(groupes.items()):
    code = "%d-%s" % (p, groupe)
    if cibles and code not in cibles:
        continue
    lignes, ids = [], {}
    for slug, nom, taxon in especes:
        cands = candidates(taxon)
        ids[slug] = [c["id"] for c in cands]
        lignes.append((nom, taxon, cands))
        time.sleep(0.4)
    chemin = planche("candidats-p%d-%s.jpg" % (p, groupe), lignes)
    index.update(ids)
    print("%s → %s" % (code, chemin))

json.dump(index, open(os.path.join(DOSSIER, "candidats-index.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("identifiants : %s/candidats-index.json" % DOSSIER)
