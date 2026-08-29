# -*- coding: utf-8 -*-
"""Propose des photographies de remplacement pour une espèce de l'imagier.

L'image d'illustration de l'article Wikipédia en français convient la plupart
du temps pour les animaux, mais c'est souvent une **planche botanique
ancienne** pour les fleurs. Ce script rassemble, pour chaque espèce demandée,
des candidates : image d'illustration de l'article anglais, puis
photographies de la catégorie Commons de l'espèce. Il en fabrique une planche
contact numérotée, à regarder avant de renseigner OVERRIDES dans
scripts/imagier-manifest.py.

Usage : python3 scripts/candidats-imagier.py <slug> [<slug> ...]
Sortie : <DOSSIER>/candidats-<slug>.jpg  et  <DOSSIER>/candidats-<slug>.json
         (DOSSIER : variable d'environnement CANDIDATS_DIR, /tmp par défaut)
"""
import io, json, math, os, re, ssl, sys, time, urllib.parse, urllib.request, urllib.error
from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
ns = {}
exec(compile(open(os.path.join(ICI, "imagier-manifest.py"), encoding="utf-8").read(),
             "imagier-manifest.py", "exec"), ns)
PAR_SLUG = {s: (p, g, n, a) for p, g, s, n, a in ns["entrees"]()}
DOSSIER = os.environ.get("CANDIDATS_DIR", "/tmp")
NB = int(os.environ.get("NB_CANDIDATS", "8"))

# Une image dont le nom de fichier ressemble à ceci est presque toujours une
# planche dessinée ou un schéma, inutilisable pour un imagier photographique.
DESSIN = re.compile(
    r"sturm|thom[ée]|koehler|lindman|illustration|plate\b|drawing|dessin|"
    r"flora von|flore de|atlas des|\bicones?\b|masclef|bilder ur|"
    r"british entomology|naturgeschichte|planche|gravure|diagram|schema|"
    r"botanical|herbari|zeichnung|nordens flora|deutschlands flora", re.I)

cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "GS-imagier/1.0 (usage pedagogique)")]


def api(hote, params):
    url = "https://%s/w/api.php?%s" % (hote, urllib.parse.urlencode(dict(params, format="json")))
    for attente in (0, 15, 40, 80):
        if attente:
            time.sleep(attente)
        try:
            with opener.open(url, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
    raise RuntimeError("429 persistant")


def article_anglais(article_fr):
    d = api("fr.wikipedia.org", {"action": "query", "titles": article_fr, "redirects": "1",
                                 "prop": "langlinks", "lllang": "en"})
    for p in d.get("query", {}).get("pages", {}).values():
        for ll in p.get("langlinks", []):
            return ll["*"]
    return None


def image_article(hote, article):
    d = api(hote, {"action": "query", "titles": article, "redirects": "1",
                   "prop": "pageimages", "piprop": "name"})
    for p in d.get("query", {}).get("pages", {}).values():
        if p.get("pageimage"):
            return "File:" + p["pageimage"]
    return None


def categorie_commons(article_fr):
    """Catégorie Commons de l'espèce, via la propriété P373 de Wikidata."""
    d = api("www.wikidata.org", {"action": "wbgetentities", "sites": "frwiki",
                                 "titles": article_fr, "props": "claims"})
    for ent in (d.get("entities") or {}).values():
        for c in ent.get("claims", {}).get("P373", []):
            val = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            if val:
                return "Category:" + val
    return None


def fichiers_categorie(categorie, limite=40):
    d = api("commons.wikimedia.org", {"action": "query", "list": "categorymembers",
                                      "cmtitle": categorie, "cmtype": "file",
                                      "cmlimit": str(limite)})
    return [m["title"] for m in d.get("query", {}).get("categorymembers", [])]


def vignettes(titres, largeur=420):
    d = api("commons.wikimedia.org", {"action": "query", "titles": "|".join(titres),
                                      "prop": "imageinfo", "iiprop": "url|mime|extmetadata",
                                      "iiurlwidth": str(largeur)})
    infos = {}
    for p in d.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [None])[0]
        if ii and ii.get("mime", "").startswith("image/"):
            infos[p["title"]] = ii.get("thumburl") or ii.get("url")
    return infos


def planche(slug, candidats):
    """Grille numérotée des candidates, à regarder avant de choisir."""
    cell, leg, cols = 420, 46, 4
    rows = max(1, math.ceil(len(candidats) / cols))
    img = Image.new("RGB", (cols * cell, rows * (cell + leg)), "white")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    for i, (titre, url) in enumerate(candidats):
        cx, cy = (i % cols) * cell, (i // cols) * (cell + leg)
        try:
            with opener.open(url, timeout=60) as r:
                v = Image.open(io.BytesIO(r.read())).convert("RGB")
            v.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
            img.paste(v, (cx + (cell - v.width) // 2, cy + (cell - v.height) // 2))
        except Exception as e:
            d.text((cx + 10, cy + 10), "échec : %s" % e, fill="red", font=f)
        d.rectangle([cx, cy, cx + cell - 1, cy + cell + leg - 1], outline="#bbb")
        d.text((cx + 8, cy + cell + 10), "%d. %s" % (i + 1, titre[5:45]), fill="black", font=f)
    chemin = os.path.join(DOSSIER, "candidats-%s.jpg" % slug)
    img.save(chemin, "JPEG", quality=85)
    return chemin


for slug in sys.argv[1:]:
    if slug not in PAR_SLUG:
        print("slug inconnu : %s" % slug)
        continue
    periode, groupe, nom, article = PAR_SLUG[slug]
    titres = []
    en = article_anglais(article)
    if en:
        t = image_article("en.wikipedia.org", en)
        if t:
            titres.append(t)
    cat = categorie_commons(article)
    if cat:
        for t in fichiers_categorie(cat):
            if t not in titres and not DESSIN.search(t):
                titres.append(t)
    titres = titres[:NB]
    if not titres:
        print("✗ %s : aucune candidate (article « %s »)" % (slug, article))
        continue
    infos = vignettes(titres)
    candidats = [(t, infos[t]) for t in titres if t in infos]
    chemin = planche(slug, candidats)
    json.dump([t for t, _ in candidats], open(os.path.join(DOSSIER, "candidats-%s.json" % slug),
                                              "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("✓ %-24s (%s) %d candidates → %s" % (slug, nom, len(candidats), chemin))
