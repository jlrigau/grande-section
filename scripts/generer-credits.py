# -*- coding: utf-8 -*-
"""Ajoute (ou régénère) la page « Crédits des images » à la fin de chaque
cahier de fiches, à partir des images réellement utilisées et de
site/fiches/img/credits.json (source Wikimedia Commons, auteur, licence).
"""
import json, os, re

BASE = os.path.join(os.path.dirname(__file__), "..", "site", "fiches")
credits = json.load(open(os.path.join(BASE, "img", "credits.json"), encoding="utf-8"))
par_fichier = {v["fichier"]: dict(v, slug=k) for k, v in credits.items()}

FICHIERS = ["periode-%d.html" % i for i in range(1, 6)] + ["entrainement-periode-%d.html" % i for i in range(1, 6)]

for nom in FICHIERS:
    chemin = os.path.join(BASE, nom)
    txt = open(chemin, encoding="utf-8").read()
    txt = re.sub(r'\n?<!-- CREDITS -->.*?<!-- /CREDITS -->\n?', "\n", txt, flags=re.S)

    utilises = sorted(set(re.findall(r'src="img/([^"]+)"', txt)))
    lignes = []
    for f in utilises:
        info = par_fichier.get(f)
        if not info:
            continue  # images auto-fabriquées (dés, formes) : pas de crédit
        auteur = info["auteur"] or "auteur inconnu"
        lignes.append(f'<li><strong>{info["slug"]}</strong> : « {info["source"].replace("File:", "")} », {auteur}, licence {info["licence"] or "?"} — Wikimedia Commons.</li>')
    if not lignes:
        open(chemin, "w", encoding="utf-8").write(txt)
        continue

    bloc = ('<!-- CREDITS -->\n<section class="fiche credits">\n'
            '<h2>Crédits des images</h2>\n'
            '<p>Les illustrations de ce cahier proviennent de Wikimedia Commons. '
            'Merci à leurs auteurs et autrices.</p>\n<ul>\n' + "\n".join(lignes) +
            '\n</ul>\n</section>\n<!-- /CREDITS -->\n')
    txt = txt.replace("</body>", bloc + "</body>")
    open(chemin, "w", encoding="utf-8").write(txt)
    print(f"{nom} : {len(lignes)} crédits")
