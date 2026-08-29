# -*- coding: utf-8 -*-
"""Télécharge les photographies de l'imagier Montessori faune et flore.

Pour chaque espèce du manifeste, on reprend l'image d'illustration de
l'article Wikipédia en français (ou le fichier imposé dans OVERRIDES), on la
recadre au format de la zone photo des cartes et on la redimensionne pour
l'impression (1100 px de large, soit environ 300 dpi sur une carte de 95 mm),
puis on enregistre l'auteur et la licence pour la page de crédits.

Usage : python3 scripts/chercher-images-imagier.py [slug ...]
        (sans argument : toutes les espèces encore manquantes)
        FORCE=1     pour retélécharger même si l'image existe déjà ;
        RECADRER=1  pour seulement refabriquer les images à partir du cache
                    des fichiers source, sans aucun accès au réseau (utile
                    après un changement du format des cartes).
"""
import hashlib, io, json, os, re, ssl, sys, time, urllib.parse, urllib.request, urllib.error
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ICI, "imagier-manifest.py"), encoding="utf-8").read()
ns = {}
exec(compile(src, "imagier-manifest.py", "exec"), ns)
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
SRC_LARGEUR = 1400      # on télécharge plus grand pour recadrer sans perte
PAUSE_TOTALE_MAX = 4000 # s : plafond des pauses imposées par le serveur

# Wikipédia en français illustre beaucoup d'articles de plantes par une
# planche botanique ancienne : inutilisable pour un imagier photographique.
# Quand le nom du fichier trahit un dessin, on essaie l'article anglais, qui
# porte presque toujours une photographie.
DESSIN = re.compile(
    r"sturm|thom[ée]|koehler|k[öo]hler|lindman|illustration|\bplate\b|drawing|dessin|"
    r"flora von|flore de|atlas des|\bicones?\b|masclef|bilder ur|nordens flora|"
    r"naturgeschichte|planche|gravure|diagram|schema|herbari|zeichnung|"
    r"deutschlands flora|\bby [A-Z]|\.svg$", re.I)

cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "GS-imagier/1.0 (https://jlrigau.github.io/grande-section/ ; materiel pedagogique pour une classe de maternelle)")]


def ouvre(url, timeout=60):
    """GET en respectant la limitation de débit de Wikimedia.

    Les refus de l'API sont brefs (quelques secondes suffisent), mais le
    serveur de fichiers (upload.wikimedia.org) impose parfois une pause de
    plusieurs minutes qu'il annonce dans l'en-tête « Retry-After ». On la
    respecte : c'est le prix d'une moisson complète en une fois.
    """
    ladder = [0, 2, 5, 10, 20, 40, 60]
    attendu = 0
    for attente in ladder:
        if attente:
            time.sleep(attente)
        try:
            return opener.open(url, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            retry = (e.headers or {}).get("Retry-After", "")
            if retry.isdigit() and int(retry) > 60 and attendu < PAUSE_TOTALE_MAX:
                pause = min(int(retry) + 15, 660)
                print("   … débit limité, pause de %d s" % pause, flush=True)
                time.sleep(pause)
                attendu += pause
    raise RuntimeError("429 persistant")


def api(hote, params):
    url = "https://%s/w/api.php?%s" % (hote, urllib.parse.urlencode(dict(params, format="json")))
    with ouvre(url) as r:
        return json.load(r)


def sans_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def lots(seq, n=40):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def fichiers_des_articles(articles, hote="fr.wikipedia.org"):
    """Image d'illustration de chaque article, en une poignée de requêtes.
    L'API accepte 50 titres à la fois : interroger espèce par espèce ferait
    180 requêtes et déclencherait la limitation de débit de Wikimedia."""
    trouve, canonique = {}, {}
    for lot in lots(articles):
        d = api(hote, {"action": "query", "titles": "|".join(lot),
                                     "redirects": "1", "prop": "pageimages",
                                     "piprop": "name", "pilimit": "50"})
        q = d.get("query", {})
        for r in q.get("redirects", []) + q.get("normalized", []):
            canonique[r["from"]] = r["to"]
        for p in q.get("pages", {}).values():
            if p.get("pageimage"):
                trouve[p["title"]] = "File:" + p["pageimage"]
        time.sleep(2)

    def resolu(titre):
        vu = set()
        while titre in canonique and titre not in vu:
            vu.add(titre)
            titre = canonique[titre]
        return titre

    return {a: trouve.get(resolu(a)) for a in articles}


def articles_anglais(articles):
    """Titre de l'article anglais correspondant, par lots."""
    equivalent = {}
    for lot in lots(articles):
        d = api("fr.wikipedia.org", {"action": "query", "titles": "|".join(lot),
                                     "redirects": "1", "prop": "langlinks",
                                     "lllang": "en", "lllimit": "50"})
        q = d.get("query", {})
        vers = {r["from"]: r["to"] for r in q.get("redirects", []) + q.get("normalized", [])}
        depuis = {}
        for a, b in vers.items():
            depuis.setdefault(b, a)
        for p in q.get("pages", {}).values():
            for ll in p.get("langlinks", []):
                equivalent[depuis.get(p["title"], p["title"])] = ll["*"]
        time.sleep(1)
    return equivalent


def infos_des_fichiers(titres):
    """Vignette et métadonnées de chaque fichier Commons, par lots."""
    infos = {}
    for lot in lots(titres):
        d = api("commons.wikimedia.org", {"action": "query", "titles": "|".join(lot),
                                          "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime",
                                          "iiurlwidth": str(SRC_LARGEUR)})
        q = d.get("query", {})
        normal = {n["from"]: n["to"] for n in q.get("normalized", [])}
        for p in q.get("pages", {}).values():
            ii = (p.get("imageinfo") or [None])[0]
            if not ii:
                continue
            meta = ii.get("extmetadata", {})
            # Le fichier d'origine est servi depuis le cache de Wikimedia,
            # alors qu'une vignette doit être fabriquée à la demande : plus
            # rapide et bien moins sujet à la limitation de débit. On ne
            # repasse par la vignette que pour les fichiers très lourds.
            original = ii.get("url")
            vignette = ii.get("thumburl") or original
            infos[p["title"]] = {
                "source": p["title"],
                "url": original if (ii.get("size") or 0) <= 12_000_000 and original else vignette,
                "page": ii.get("descriptionurl"),
                "licence": sans_html(meta.get("LicenseShortName", {}).get("value", "")),
                "auteur": sans_html(meta.get("Artist", {}).get("value", ""))[:90],
            }
        for depuis, vers in normal.items():
            if vers in infos:
                infos.setdefault(depuis, infos[vers])
        time.sleep(2)
    return infos


def cadre(im):
    """Ramène l'image au format des cartes (11/8) : recadrage centré tant
    qu'il reste raisonnable, sinon bandes blanches, pour ne jamais couper
    l'animal ou la fleur au point de le rendre méconnaissable."""
    l, h = im.size
    r = l / float(h)
    if abs(r - RATIO) < 0.01:
        pass
    elif r > RATIO:                       # trop panoramique : on rogne les côtés
        nl = int(round(h * RATIO))
        perte = 1 - nl / float(l)
        if perte <= ROGNAGE_MAX:
            x = (l - nl) // 2
            im = im.crop((x, 0, x + nl, h))
        else:
            im = marges(im)
    else:                                  # trop en hauteur : on rogne haut/bas
        nh = int(round(l / RATIO))
        perte = 1 - nh / float(h)
        if perte <= ROGNAGE_MAX:
            # le sujet est le plus souvent dans la moitié haute : on rogne
            # davantage en bas qu'en haut
            y = int(round((h - nh) * 0.35))
            im = im.crop((0, y, l, y + nh))
        else:
            im = marges(im)
    return im


def marges(im):
    """Image entière centrée sur un fond blanc au format des cartes : on
    préfère deux bandes blanches à un animal coupé en deux."""
    l, h = im.size
    if l / float(h) > RATIO:
        l_cible, h_cible = l, int(round(l / RATIO))
    else:
        l_cible, h_cible = int(round(h * RATIO)), h
    fond = Image.new("RGB", (l_cible, h_cible), "white")
    fond.paste(im, ((l_cible - l) // 2, (h_cible - h) // 2))
    return fond


def cache_de(titre):
    """Le cache est indexé par fichier Commons, pas par espèce : changer
    l'image d'une espèce ne doit pas resservir l'ancienne."""
    return os.path.join(CACHE, hashlib.sha1(titre.encode("utf-8")).hexdigest() + ".src")


def enregistre(url, chemin, titre):
    """Le fichier source est gardé en cache : ajuster le cadrage des cartes ne
    demande alors pas de repasser par le réseau."""
    cache = cache_de(titre)
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
    im = cadre(im)
    hauteur = int(round(LARGEUR / RATIO))
    im = im.resize((LARGEUR, hauteur), Image.LANCZOS)
    im.save(chemin, "JPEG", quality=QUALITE, optimize=True, progressive=True)
    return im.size


demandes = set(sys.argv[1:])
force = os.environ.get("FORCE") == "1"
recadrer = os.environ.get("RECADRER") == "1"


a_faire = [e for e in ENTREES if not demandes or e[2] in demandes]
if not recadrer:
    a_faire = [e for e in a_faire
               if force or e[2] not in credits or not os.path.exists(os.path.join(OUT, e[2] + ".jpg"))]

# 1. Quel fichier Commons pour quelle espèce (résolution groupée).
fichiers = {}
if a_faire and not recadrer:
    a_resoudre = [e for e in a_faire if e[2] not in OVERRIDES]
    par_article = fichiers_des_articles(sorted({e[4] for e in a_resoudre}))
    # Repli sur l'article anglais quand l'illustration française est un dessin.
    suspects = sorted(a for a, t in par_article.items() if not t or DESSIN.search(t))
    if suspects:
        equivalents = articles_anglais(suspects)
        par_en = fichiers_des_articles(sorted(set(equivalents.values())), "en.wikipedia.org")
        for a in suspects:
            t = par_en.get(equivalents.get(a))
            if t and not DESSIN.search(t):
                print("→ %-28s photographie reprise de l'article anglais" % a)
                par_article[a] = t
    for periode, groupe, slug, nom, article in a_faire:
        titre = OVERRIDES.get(slug) or par_article.get(article)
        if titre and not titre.startswith("File:"):
            titre = "File:" + titre
        fichiers[slug] = titre
    infos = infos_des_fichiers(sorted({t for t in fichiers.values() if t}))
else:
    infos = {}

# 2. Fabrication des images de cartes (le fichier source est mis en cache,
#    un changement de format ne demande alors plus le réseau).
compte = {"ok": 0, "err": 0}
for periode, groupe, slug, nom, article in a_faire:
    chemin = os.path.join(OUT, slug + ".jpg")
    if recadrer:
        if slug not in credits or not os.path.exists(cache_de(credits[slug]["source"])):
            print("… %-24s absent du cache, à retélécharger" % slug)
            compte["err"] += 1
            continue
        taille = enregistre(None, chemin, credits[slug]["source"])
        credits[slug]["px"] = "%dx%d" % taille
        print("↺ %-24s recadré %dx%d" % (slug, taille[0], taille[1]))
        compte["ok"] += 1
        continue
    titre = fichiers.get(slug)
    info = infos.get(titre) if titre else None
    if not info or not info.get("url"):
        print("✗ %-24s aucune image pour « %s »" % (slug, article))
        compte["err"] += 1
        continue
    try:
        taille = enregistre(info["url"], chemin, info["source"])
    except Exception as e:
        print("✗ %-24s %s" % (slug, e))
        compte["err"] += 1
        continue
    credits[slug] = {"fichier": slug + ".jpg", "nom": nom, "periode": periode, "groupe": groupe,
                     "article": article, "source": info["source"], "page": info["page"],
                     "licence": info["licence"], "auteur": info["auteur"],
                     "px": "%dx%d" % taille}
    json.dump(credits, open(CREDITS, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("✓ P%d %-5s %-24s ← %s [%s]"
          % (periode, groupe, slug, info["source"][5:60], info["licence"]), flush=True)
    compte["ok"] += 1

json.dump(credits, open(CREDITS, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("\n%d images fabriquées, %d échecs — crédits : %s" % (compte["ok"], compte["err"], CREDITS))
