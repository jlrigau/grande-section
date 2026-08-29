# -*- coding: utf-8 -*-
"""Récupère le nom scientifique (Wikidata P225) de chaque espèce de l'imagier,
pour la liste récapitulative du mode d'emploi destinée à l'enseignante.

Sortie : site/imagier/img/taxons.json  {slug: "Nom scientifique"}
Usage  : python3 scripts/taxons-imagier.py
"""
import json, os, ssl, urllib.parse, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
ns = {}
exec(compile(open(os.path.join(ICI, "imagier-manifest.py"), encoding="utf-8").read(),
             "imagier-manifest.py", "exec"), ns)
ENTREES = list(ns["entrees"]())
SORTIE = os.path.join(ICI, "..", "site", "imagier", "img", "taxons.json")

cafile = "/root/.ccr/ca-bundle.crt"
ctx = ssl.create_default_context(cafile=cafile) if os.path.exists(cafile) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "GS-imagier/1.0 (usage pedagogique)")]


def api(hote, params):
    url = "https://%s/w/api.php?%s" % (hote, urllib.parse.urlencode(dict(params, format="json")))
    with opener.open(url, timeout=60) as r:
        return json.load(r)


def lots(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# 1. Titre canonique de chaque article (les redirections faussent Wikidata).
canonique = {}
articles = [e[4] for e in ENTREES]
for lot in lots(articles, 40):
    d = api("fr.wikipedia.org", {"action": "query", "titles": "|".join(lot), "redirects": "1"})
    q = d.get("query", {})
    for r in q.get("redirects", []):
        canonique[r["from"]] = r["to"]
    for n in q.get("normalized", []):
        canonique.setdefault(n["from"], n["to"])

def resolu(titre):
    vu = set()
    while titre in canonique and titre not in vu:
        vu.add(titre)
        titre = canonique[titre]
    return titre

# 2. Nom scientifique (P225) de l'élément Wikidata lié à l'article.
par_titre = {}
titres = sorted({resolu(a) for a in articles})
for lot in lots(titres, 40):
    d = api("www.wikidata.org", {"action": "wbgetentities", "sites": "frwiki",
                                 "titles": "|".join(lot), "props": "claims|sitelinks"})
    for ent in (d.get("entities") or {}).values():
        if "missing" in ent:
            continue
        titre = (ent.get("sitelinks", {}).get("frwiki") or {}).get("title")
        claims = ent.get("claims", {}).get("P225") or []
        for c in claims:
            val = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            if val and titre:
                par_titre[titre] = val
                break

taxons = {}
manquants = []
for periode, groupe, slug, nom, article in ENTREES:
    t = par_titre.get(resolu(article))
    if t:
        taxons[slug] = t
    else:
        manquants.append((slug, article))

json.dump(taxons, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("%d noms scientifiques → %s" % (len(taxons), SORTIE))
for slug, article in manquants:
    print("  (sans nom scientifique : %s — « %s »)" % (slug, article))
