# -*- coding: utf-8 -*-
"""Télécharge depuis Wikimedia Commons une image par concept du manifeste,
avec ses métadonnées (auteur, licence) pour la page de crédits.
Usage : python3 scripts/chercher-images.py [slug ...]   (sans argument : tout)
Sortie : site/fiches/img/<slug>.(png|jpg) + site/fiches/img/credits.json
"""
import json, os, re, ssl, sys, time, urllib.parse, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module
MANIFEST = import_module("images-manifest".replace("-", "_")) if False else None
# le nom de fichier contient un tiret : chargement manuel
manifest_src = open(os.path.join(os.path.dirname(__file__), "images-manifest.py"), encoding="utf-8").read()
ns = {}
exec(manifest_src, ns)
MANIFEST = ns["MANIFEST"]

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "fiches", "img")
os.makedirs(OUT, exist_ok=True)
CREDITS_PATH = os.path.join(OUT, "credits.json")
credits = json.load(open(CREDITS_PATH, encoding="utf-8")) if os.path.exists(CREDITS_PATH) else {}

ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "GS-fiches/1.0 (usage pedagogique)")]

API = "https://commons.wikimedia.org/w/api.php"

def ouvre(url, timeout=30):
    """GET avec reprise sur 429 (limitation de débit)."""
    for attente in (0, 25, 50, 90):
        if attente:
            time.sleep(attente)
        try:
            return opener.open(url, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
    raise RuntimeError("429 persistant")

def api(params):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    with ouvre(url) as r:
        return json.load(r)

def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()

def infos_fichier(titre):
    d = api({"action": "query", "titles": titre, "prop": "imageinfo",
             "iiprop": "url|extmetadata|mime", "iiurlwidth": "260"})
    pages = d.get("query", {}).get("pages", {})
    for p in pages.values():
        ii = (p.get("imageinfo") or [None])[0]
        if ii:
            meta = ii.get("extmetadata", {})
            return {
                "titre": p.get("title"),
                "thumb": ii.get("thumburl") or ii.get("url"),
                "page": ii.get("descriptionurl"),
                "licence": strip_html(meta.get("LicenseShortName", {}).get("value", "")),
                "auteur": strip_html(meta.get("Artist", {}).get("value", ""))[:80],
            }
    return None

def cherche(query):
    if query.startswith("File:"):
        return infos_fichier(query)
    d = api({"action": "query", "generator": "search",
             "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": "8",
             "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": "260"})
    pages = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in pages:
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        mime = ii.get("mime", "")
        if mime not in ("image/jpeg", "image/png", "image/svg+xml", "image/gif"):
            continue
        meta = ii.get("extmetadata", {})
        return {
            "titre": p.get("title"),
            "thumb": ii.get("thumburl") or ii.get("url"),
            "page": ii.get("descriptionurl"),
            "licence": strip_html(meta.get("LicenseShortName", {}).get("value", "")),
            "auteur": strip_html(meta.get("Artist", {}).get("value", ""))[:80],
        }
    return None

def telecharge(url, chemin):
    with ouvre(url, timeout=60) as r, open(chemin, "wb") as f:
        f.write(r.read())

slugs = sys.argv[1:] or list(MANIFEST.keys())
ok = err = 0
for slug in slugs:
    if slug in credits and os.path.exists(os.path.join(OUT, credits[slug]["fichier"])):
        continue  # déjà téléchargée
    q = MANIFEST[slug]
    time.sleep(4)
    try:
        info = cherche(q)
        if not info or not info.get("thumb"):
            print(f"✗ {slug}: aucun résultat pour « {q} »"); err += 1; continue
        ext = ".jpg" if ".jpg" in info["thumb"].lower() or ".jpeg" in info["thumb"].lower() else ".png"
        chemin = os.path.join(OUT, slug + ext)
        for autre in (".jpg", ".png"):
            a = os.path.join(OUT, slug + autre)
            if a != chemin and os.path.exists(a):
                os.remove(a)
        telecharge(info["thumb"], chemin)
        credits[slug] = {"fichier": slug + ext, "source": info["titre"], "page": info["page"],
                         "licence": info["licence"], "auteur": info["auteur"]}
        print(f"✓ {slug} ← {info['titre']} [{info['licence']}]"); ok += 1
    except Exception as e:
        print(f"✗ {slug}: {e}"); err += 1

json.dump(credits, open(CREDITS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n{ok} images téléchargées, {err} échecs. Crédits : {CREDITS_PATH}")
