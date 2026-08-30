# -*- coding: utf-8 -*-
"""Chercher, regarder puis installer un pictogramme pour les fiches élève.

Trois commandes :

  # 1 — chercher des candidats (Mulberry + ARASAAC) et fabriquer une planche
  python3 scripts/chercher-pictos.py chercher poule "hen chicken"
  #   1er argument après « chercher » : le slug (nom du fichier cible)
  #   2e : les mots-clés ANGLAIS pour Mulberry (cherchés dans le nom des
  #        3436 pictos) ; la recherche ARASAAC utilise le slug (français),
  #        sauf si ARASAAC=<mot> le remplace (accents permis)
  #   → candidats dans /tmp/pictos/<slug>/, planche /tmp/pictos/<slug>.png

  # 2 — installer le candidat retenu : copie dans site/fiches/img/ et
  #     inscrit la source, la licence et l'auteur dans credits.json
  python3 scripts/chercher-pictos.py installer poule mulberry:hen
  python3 scripts/chercher-pictos.py installer poule arasaac:2403

  # 3 — vérifier la banque : crédits complets, fichiers orphelins,
  #     images référencées manquantes
  python3 scripts/chercher-pictos.py verifier

Ne JAMAIS installer un candidat sans avoir regardé la planche : les noms
mentent (« chicken » Mulberry est un poulet rôti, « dove » une colombe,
« plane » un rabot). Le skill fiches-illustrations raconte les pièges.
"""
import json, os, re, ssl, subprocess, sys, urllib.parse, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ICI, "..", "site", "fiches", "img")
CACHE = os.environ.get("PICTOS_DIR", "/tmp/pictos")
MULB_VERSION = "3.5.2"
CA = "/root/.ccr/ca-bundle.crt"

ctx = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
opener = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "Mozilla/5.0 (fiches pedagogiques GS)")]


def telecharge(url, chemin=None, timeout=40):
    with opener.open(url, timeout=timeout) as r:
        donnees = r.read()
    if chemin:
        open(chemin, "wb").write(donnees)
    return donnees


def catalogue_mulberry():
    """La liste des noms EN de Mulberry, mise en cache (GitHub est bloqué
    par le proxy de l'agent ; jsDelivr passe)."""
    c = os.path.join(CACHE, "mulberry-%s.json" % MULB_VERSION)
    if not os.path.exists(c):
        os.makedirs(CACHE, exist_ok=True)
        d = json.loads(telecharge(
            "https://data.jsdelivr.com/v1/packages/gh/mulberrysymbols/mulberry-symbols@" + MULB_VERSION))
        def parcours(noeud, prefixe=""):
            for f in noeud.get("files", []):
                if "files" in f:
                    yield from parcours(f, prefixe + f.get("name", "") + "/")
                else:
                    yield prefixe + f.get("name", "")
        noms = [n.split("/")[-1][:-4] for n in parcours(d)
                if ("EN/" in n and not n.split("EN/")[0].strip("/")) and n.endswith(".svg")]
        json.dump(noms, open(c, "w"))
    return json.load(open(c))


def url_mulberry(nom):
    return ("https://cdn.jsdelivr.net/gh/mulberrysymbols/mulberry-symbols@"
            + MULB_VERSION + "/EN/" + urllib.parse.quote(nom) + ".svg")


def chercher(slug, cles_en):
    dossier = os.path.join(CACHE, slug)
    os.makedirs(dossier, exist_ok=True)
    trouves = []

    # — Mulberry : recherche dans les noms —
    noms = catalogue_mulberry()
    motifs = [m.lower() for m in cles_en.split()]
    hits = [n for n in noms if any(m in n.lower() for m in motifs)][:10]
    for n in hits:
        f = os.path.join(dossier, "mulberry_" + n.replace(",", "_") + ".svg")
        try:
            telecharge(url_mulberry(n), f)
            trouves.append(("mulberry:" + n, f, "CC BY-SA 4.0"))
        except Exception as e:
            print("  mulberry", n, ":", e)

    # — ARASAAC : recherche en français —
    mot = os.environ.get("ARASAAC", slug)
    try:
        d = json.loads(telecharge(
            "https://api.arasaac.org/api/pictograms/fr/search/" + urllib.parse.quote(mot)))
    except Exception as e:
        print("  arasaac :", e)
        d = []
    for x in d[:6]:
        pid = x["_id"]
        kw = ", ".join(str(k.get("keyword")) for k in x.get("keywords", [])[:2])
        f = os.path.join(dossier, "arasaac_%d.png" % pid)
        try:
            telecharge("https://static.arasaac.org/pictograms/%d/%d_500.png" % (pid, pid), f)
            trouves.append(("arasaac:%d (%s)" % (pid, kw), f, "CC BY-NC-SA"))
        except Exception as e:
            print("  arasaac", pid, ":", e)

    if not trouves:
        print("aucun candidat — élargir les mots-clés, ou Openverse en dernier recours")
        return

    # — la planche, à regarder AVANT de choisir —
    cellules = "".join(
        '<div class="c"><img src="%s"><div>%s<br><small>%s</small></div></div>'
        % (os.path.abspath(f), ident, lic) for ident, f, lic in trouves)
    html = os.path.join(CACHE, slug + ".html")
    open(html, "w", encoding="utf-8").write(
        '<meta charset="utf-8"><style>body{font:12px sans-serif}'
        '.g{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}'
        '.c{border:1px solid #ccc;text-align:center;padding:5px}'
        '.c img{width:130px;height:130px;object-fit:contain}</style>'
        "<h3>%s — juger chaque image, ne pas se fier aux noms</h3>"
        '<div class="g">%s</div>' % (slug, cellules))
    png = os.path.join(CACHE, slug + ".png")
    chromes = [p for p in
               subprocess.run(["sh", "-c", "ls -d /opt/pw-browsers/chromium*/chrome-linux/chrome 2>/dev/null"],
                              capture_output=True, text=True).stdout.split() ]
    if chromes:
        subprocess.run([chromes[0], "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--screenshot=" + png,
                        "--window-size=800,%d" % (200 + 190 * (1 + len(trouves) // 5)),
                        "file://" + html], capture_output=True)
        print("planche : %s" % png)
    else:
        print("planche : %s (pas de Chromium trouvé pour le PNG)" % html)
    for ident, f, lic in trouves:
        print("  %-40s %s" % (ident, lic))


CRED_MULBERRY = {"source": "Mulberry Symbols", "page": "https://mulberrysymbols.org/",
                 "licence": "CC BY-SA 4.0", "auteur": "Paxtoncrafts Charitable Trust"}


def installer(slug, choix):
    credits = json.load(open(os.path.join(IMG, "credits.json"), encoding="utf-8"))
    if choix.startswith("mulberry:"):
        nom = choix.split(":", 1)[1]
        dest = slug + ".svg"
        telecharge(url_mulberry(nom), os.path.join(IMG, dest))
        credits[slug] = dict(fichier=dest, **CRED_MULBERRY)
    elif choix.startswith("arasaac:"):
        pid = int(choix.split(":", 1)[1].split()[0])
        dest = slug + ".png"
        telecharge("https://static.arasaac.org/pictograms/%d/%d_500.png" % (pid, pid),
                   os.path.join(IMG, dest))
        credits[slug] = {"fichier": dest, "source": "ARASAAC",
                         "page": "https://arasaac.org/pictograms/fr/%d" % pid,
                         "licence": "CC BY-NC-SA",
                         "auteur": "Sergio Palao — propriété du Gouvernement d’Aragon (Espagne)"}
    else:
        sys.exit("choix attendu : mulberry:<nom> ou arasaac:<id>")
    # une seule extension par slug : purger l'ancienne version
    for ext in (".svg", ".png", ".jpg", ".jpeg"):
        f = os.path.join(IMG, slug + ext)
        if os.path.exists(f) and slug + ext != dest:
            os.remove(f)
            print("supprimé :", slug + ext)
    json.dump(credits, open(os.path.join(IMG, "credits.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("installé : img/%s — penser à : generer-credits.py, contrôle PDF" % dest)


AUTO = {"de-1", "de-2", "de-3", "de-4", "de-5", "de-6",
        "rond", "rond-plein", "triangle", "etoile-jaune", "seau", "pelle"}


def verifier():
    credits = json.load(open(os.path.join(IMG, "credits.json"), encoding="utf-8"))
    fichiers = {f for f in os.listdir(IMG) if f != "credits.json"}
    soucis = 0
    for slug, c in credits.items():
        if c["fichier"] not in fichiers:
            print("crédit sans fichier :", slug, "→", c["fichier"]); soucis += 1
        for champ in ("source", "licence", "auteur"):
            if not c.get(champ):
                print("crédit incomplet :", slug, "(", champ, ")"); soucis += 1
    references = set()
    dossier_fiches = os.path.join(IMG, "..")
    for nom in os.listdir(dossier_fiches):
        if nom.endswith(".html"):
            txt = open(os.path.join(dossier_fiches, nom), encoding="utf-8").read()
            for m in re.findall(r'src="img/([^"]+)"', txt):
                references.add(m)
                if m not in fichiers:
                    print("image référencée absente :", nom, "→", m); soucis += 1
    par_credit = {c["fichier"] for c in credits.values()}
    for f in sorted(fichiers - par_credit):
        if f.rsplit(".", 1)[0] not in AUTO:
            print("fichier sans crédit :", f); soucis += 1
    for f in sorted(fichiers - references):
        print("fichier jamais référencé (à supprimer ?) :", f)
    print("OK" if not soucis else "%d problème(s)" % soucis)
    sys.exit(1 if soucis else 0)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "chercher":
        chercher(sys.argv[2], " ".join(sys.argv[3:]))
    elif len(sys.argv) == 4 and sys.argv[1] == "installer":
        installer(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "verifier":
        verifier()
    else:
        sys.exit(__doc__)
