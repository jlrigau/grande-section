# -*- coding: utf-8 -*-
"""Télécharge les photographies de l'imagier Montessori faune et flore.

Source : iNaturalist. On ne retient que des observations de « qualité
recherche » — l'espèce a été confirmée par plusieurs naturalistes — et des
photographies sous licence libre (CC0, CC BY, CC BY-SA), ce qui autorise la
publication sur le site de la classe avec mention de l'auteur.

Ne pas revenir à Wikimedia Commons : son serveur de fichiers limite l'adresse
de sortie de l'agent à quelques images par tranche de dix minutes, ce qui met
des heures pour les quatre-vingt-dix cartes. iNaturalist les fabrique en
quelques minutes. Les espèces sont cherchées par leur nom scientifique, porté
par le manifeste, une recherche par nom vernaculaire étant peu fiable.

Le classement d'iNaturalist met en avant de belles photographies, pas
forcément illustratives : la photographie de chaque espèce est choisie à la
main et inscrite dans OVERRIDES (voir scripts/candidats-imagier.py).

Chaque photographie est recadrée au format de la zone photo des cartes et
enregistrée en 1100 px de large, soit environ 300 dpi à l'impression.

Usage : python3 scripts/chercher-images-imagier.py [slug ...]
        (sans argument : toutes les espèces encore manquantes)
        FORCE=1     retélécharge même si l'image existe déjà ;
        RECADRER=1  refabrique les images depuis le cache des fichiers
                    source, sans aucun accès au réseau (utile après un
                    changement du format des cartes).
"""
import io, json, os, ssl, sys, time, urllib.error, urllib.parse, urllib.request
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
ns = {}
exec(compile(open(os.path.join(ICI, "imagier-manifest.py"), encoding="utf-8").read(),
             "imagier-manifest.py", "exec"), ns)
ENTREES = list(ns["entrees"]())
OVERRIDES = ns["OVERRIDES"]

OUT = os.path.join(ICI, "..", "site", "imagier", "img")
os.makedirs(OUT, exist_ok=True)
CREDITS = os.path.join(OUT, "credits.json")
CACHE = os.environ.get("IMAGIER_CACHE", "/tmp/imagier-source")
os.makedirs(CACHE, exist_ok=True)
credits = json.load(open(CREDITS, encoding="utf-8")) if os.path.exists(CREDITS) else {}

LARGEUR = 1100          # px : ~300 dpi sur la zone photo d'une carte (90,6 mm)
RATIO = 1.46            # proportion de la zone photo des cartes (90,6 x 62 mm)
ROGNAGE_MAX = 0.45      # au-delà, on préfère des bandes blanches à une coupe
QUALITE = 84
MIN_COTE = 1000         # px : en deçà, la photo est trop petite pour imprimer
LICENCES = "cc0,cc-by,cc-by-sa"

API = "https://api.inaturalist.org/v1/observations"
cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "GS-imagier/1.0 (https://jlrigau.github.io/grande-section/ ; "
                                    "materiel pedagogique pour une classe de maternelle)")]


def ouvre(url, timeout=45):
    """GET avec quelques reprises sur 429 et 5xx."""
    for attente in (0, 3, 8, 20, 45):
        if attente:
            time.sleep(attente)
        try:
            return opener.open(url, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
    raise RuntimeError("serveur indisponible après plusieurs tentatives")


def candidates(taxon, recherche_seule=True):
    """Photographies libres et assez grandes pour l'impression, les mieux
    notées d'abord. Les animaux domestiques n'ont pas d'observation de
    « qualité recherche » (ils ne sont pas sauvages) : on relâche alors ce
    critère."""
    params = {"taxon_name": taxon, "photo_license": LICENCES, "photos": "true",
              "order_by": "votes", "per_page": "24", "locale": "fr"}
    if recherche_seule:
        params["quality_grade"] = "research"
    with ouvre(API + "?" + urllib.parse.urlencode(params)) as r:
        d = json.load(r)
    trouve = []
    for obs in d.get("results", []):
        for photo in obs.get("photos", []):
            dim = photo.get("original_dimensions") or {}
            l, h = dim.get("width", 0), dim.get("height", 0)
            if min(l, h) < MIN_COTE:
                continue
            trouve.append({
                "id": photo["id"],
                "url": photo["url"].replace("square", "original"),
                "licence": (photo.get("license_code") or "").upper().replace("CC-", "CC "),
                "auteur": nettoie_attribution(photo.get("attribution", "")),
                "observation": "https://www.inaturalist.org/observations/%s" % obs["id"],
                "px": "%dx%d" % (l, h),
                "paysage": l >= h,
            })
    if not trouve and recherche_seule:
        return candidates(taxon, recherche_seule=False)
    # à qualité égale, une photo en largeur remplit mieux la carte
    trouve.sort(key=lambda p: not p["paysage"])
    return trouve


def nettoie_attribution(a):
    """« (c) Nom, some rights reserved (CC BY), uploaded by … » → « Nom »."""
    a = a.split(", some rights reserved")[0].split(", no rights reserved")[0]
    a = a.split(", all rights reserved")[0]
    return a.replace("(c)", "").replace("©", "").strip() or "auteur non précisé"


def cadre(im):
    """Ramène l'image au format des cartes : recadrage centré tant qu'il
    reste raisonnable, sinon bandes blanches, pour ne jamais couper la
    plante ou l'animal au point de le rendre méconnaissable."""
    l, h = im.size
    r = l / float(h)
    if abs(r - RATIO) < 0.01:
        return im
    if r > RATIO:                          # trop panoramique : on rogne les côtés
        nl = int(round(h * RATIO))
        if 1 - nl / float(l) <= ROGNAGE_MAX:
            x = (l - nl) // 2
            return im.crop((x, 0, x + nl, h))
    else:                                  # trop en hauteur : on rogne haut et bas
        nh = int(round(l / RATIO))
        if 1 - nh / float(h) <= ROGNAGE_MAX:
            # le sujet est le plus souvent dans la moitié haute
            y = int(round((h - nh) * 0.35))
            return im.crop((0, y, l, y + nh))
    return marges(im)


def marges(im):
    """Image entière centrée sur un fond blanc au format des cartes."""
    l, h = im.size
    if l / float(h) > RATIO:
        cible = (l, int(round(l / RATIO)))
    else:
        cible = (int(round(h * RATIO)), h)
    fond = Image.new("RGB", cible, "white")
    fond.paste(im, ((cible[0] - l) // 2, (cible[1] - h) // 2))
    return fond


def credits_photo(taxon, photo_id):
    """Retrouve l'auteur et la licence d'une photographie imposée, en
    parcourant plus largement les observations de l'espèce."""
    for tri in ("votes", "created_at"):
        for grade in (None, "research"):
            params = {"taxon_name": taxon, "photo_license": LICENCES, "photos": "true",
                      "order_by": tri, "per_page": "60"}
            if grade:
                params["quality_grade"] = grade
            with ouvre(API + "?" + urllib.parse.urlencode(params)) as r:
                d = json.load(r)
            for obs in d.get("results", []):
                for ph in obs.get("photos", []):
                    if ph["id"] != photo_id:
                        continue
                    dim = ph.get("original_dimensions") or {}
                    return {"id": ph["id"], "url": ph["url"].replace("square", "original"),
                            "licence": (ph.get("license_code") or "").upper().replace("CC-", "CC "),
                            "auteur": nettoie_attribution(ph.get("attribution", "")),
                            "observation": "https://www.inaturalist.org/observations/%s" % obs["id"],
                            "px": "%dx%d" % (dim.get("width", 0), dim.get("height", 0))}
    return None


def url_photo(photo_id):
    """URL d'une photographie dont on ne connaît que l'identifiant : iNaturalist
    la sert depuis deux hôtes et sous plusieurs extensions."""
    for hote in ("https://inaturalist-open-data.s3.amazonaws.com/photos",
                 "https://static.inaturalist.org/photos"):
        for ext in ("jpeg", "jpg", "png"):
            url = "%s/%s/original.%s" % (hote, photo_id, ext)
            try:
                with ouvre(url, timeout=30) as r:
                    r.read(1)
                return url
            except urllib.error.HTTPError:
                continue
    raise RuntimeError("photographie %s introuvable" % photo_id)


def cache_de(photo_id):
    return os.path.join(CACHE, "inat-%s.src" % photo_id)


def enregistre(url, chemin, photo_id):
    """Le fichier source est gardé en cache : ajuster le cadrage des cartes
    ne demande alors pas de repasser par le réseau."""
    cache = cache_de(photo_id)
    if os.path.exists(cache) and os.path.getsize(cache) > 0:
        brut = open(cache, "rb").read()
    else:
        with ouvre(url) as r:
            brut = r.read()
        open(cache, "wb").write(brut)
    im = Image.open(io.BytesIO(brut))
    if im.mode in ("RGBA", "LA", "P"):
        fond = Image.new("RGB", im.size, "white")
        im = im.convert("RGBA")
        fond.paste(im, mask=im.split()[-1])
        im = fond
    else:
        im = im.convert("RGB")
    im = cadre(im).resize((LARGEUR, int(round(LARGEUR / RATIO))), Image.LANCZOS)
    im.save(chemin, "JPEG", quality=QUALITE, optimize=True, progressive=True)
    return im.size


demandes = set(sys.argv[1:])
force = os.environ.get("FORCE") == "1"
recadrer = os.environ.get("RECADRER") == "1"

a_faire = [e for e in ENTREES if not demandes or e[2] in demandes]
if not recadrer:
    a_faire = [e for e in a_faire
               if force or e[2] not in credits or not os.path.exists(os.path.join(OUT, e[2] + ".jpg"))]

compte = {"ok": 0, "err": 0}
for periode, groupe, slug, nom, taxon in a_faire:
    chemin = os.path.join(OUT, slug + ".jpg")
    if recadrer:
        if slug not in credits or not os.path.exists(cache_de(credits[slug]["photo_id"])):
            print("… %-24s absent du cache, à retélécharger" % slug)
            compte["err"] += 1
            continue
        taille = enregistre(None, chemin, credits[slug]["photo_id"])
        print("↺ %-24s recadré %dx%d" % (slug, taille[0], taille[1]))
        compte["ok"] += 1
        continue
    try:
        impose = OVERRIDES.get(slug)
        photos = candidates(taxon)
        photo = None
        if impose:
            photo = next((p for p in photos if p["id"] == impose), None)
            if photo is None:                    # photo imposée hors du premier lot
                photo = credits_photo(taxon, impose) or {
                    "id": impose, "url": url_photo(impose),
                    "licence": "", "auteur": "", "observation": "", "px": ""}
        elif photos:
            photo = photos[0]
        if photo is None:
            print("✗ %-24s aucune photo libre assez grande pour « %s »" % (slug, taxon))
            compte["err"] += 1
            continue
        taille = enregistre(photo["url"], chemin, photo["id"])
        credits[slug] = {"fichier": slug + ".jpg", "nom": nom, "periode": periode, "groupe": groupe,
                         "taxon": taxon, "photo_id": photo["id"], "auteur": photo["auteur"],
                         "licence": photo["licence"], "observation": photo["observation"],
                         "source_px": photo["px"], "px": "%dx%d" % taille}
        json.dump(credits, open(CREDITS, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        print("✓ P%d %-5s %-24s %-28s %s [%s]"
              % (periode, groupe, slug, taxon, photo["auteur"][:28], photo["licence"]), flush=True)
        compte["ok"] += 1
    except Exception as e:
        print("✗ %-24s %s" % (slug, e), flush=True)
        compte["err"] += 1
    time.sleep(0.5)

json.dump(credits, open(CREDITS, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("\n%d images fabriquées, %d échecs — crédits : %s" % (compte["ok"], compte["err"], CREDITS))
