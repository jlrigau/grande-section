# -*- coding: utf-8 -*-
"""Manifeste de l'imagier Montessori « faune et flore ».

Pour chaque période (milieu) : au moins 9 espèces de faune et 9 espèces de
fleurs. Chaque entrée décrit :
  slug     — nom de fichier de l'image (sans extension) ;
  nom      — le mot écrit sur l'étiquette (script, minuscules) ;
  article  — le titre exact de l'article Wikipédia en français, dont on
             reprend l'image d'illustration (photographie de l'espèce) ;
  file     — (facultatif) nom de fichier Commons imposé, quand l'image
             d'illustration de l'article ne convient pas.

Utilisé par scripts/chercher-images-imagier.py (téléchargement + crédits)
et par scripts/generer-imagier.py (génération des planches HTML).
"""

MILIEUX = [
    (1, "ville",    "🏙️", "La ville",    "Les animaux et les fleurs de la ville, des parcs et des balcons."),
    (2, "foret",    "🌳", "La forêt",    "Les animaux et les fleurs des bois et des sous-bois."),
    (3, "montagne", "⛰️", "La montagne", "Les animaux et les fleurs de l’étage alpin."),
    (4, "campagne", "🌾", "La campagne", "Les animaux de la ferme et des prés, les fleurs des champs."),
    (5, "mer",      "🌊", "La mer",      "Les animaux du bord de mer et les fleurs du littoral."),
]

IMAGIER = {
 1: {
  "faune": [
   ("pigeon-biset",          "le pigeon biset",          "Pigeon biset"),
   ("moineau-domestique",    "le moineau domestique",    "Moineau domestique"),
   ("merle-noir",            "le merle noir",            "Merle noir"),
   ("mesange-charbonniere",  "la mésange charbonnière",  "Mésange charbonnière"),
   ("martinet-noir",         "le martinet noir",         "Martinet noir"),
   ("herisson-europe",       "le hérisson",              "Hérisson d'Europe"),
   ("ecureuil-roux",         "l’écureuil roux",          "Écureuil roux"),
   ("coccinelle-7-points",   "la coccinelle",            "Coccinelle à sept points"),
   ("abeille-domestique",    "l’abeille",                "Abeille européenne"),
  ],
  "flore": [
   ("paquerette",            "la pâquerette",            "Pâquerette"),
   ("pissenlit",             "le pissenlit",             "Pissenlit"),
   ("rosier",                "la rose",                  "Rosier"),
   ("tulipe",                "la tulipe",                "Tulipe"),
   ("geranium-balcon",       "le géranium",              "Pelargonium"),
   ("pensee",                "la pensée",                "Pensée (fleur)"),
   ("lavande",               "la lavande",               "Lavande"),
   ("begonia",               "le bégonia",               "Begonia"),
   ("rose-tremiere",         "la rose trémière",         "Rose trémière"),
  ],
 },
 2: {
  "faune": [
   ("cerf-elaphe",           "le cerf",                  "Cerf élaphe"),
   ("chevreuil",             "le chevreuil",             "Chevreuil européen"),
   ("sanglier",              "le sanglier",              "Sanglier"),
   ("renard-roux",           "le renard roux",           "Renard roux"),
   ("blaireau-europeen",     "le blaireau",              "Blaireau européen"),
   ("chouette-hulotte",      "la chouette hulotte",      "Chouette hulotte"),
   ("pic-vert",              "le pic vert",              "Pic vert"),
   ("salamandre-tachetee",   "la salamandre",            "Salamandre tachetée"),
   ("fourmi-rousse",         "la fourmi rousse",         "Formica rufa"),
  ],
  "flore": [
   ("jacinthe-des-bois",     "la jacinthe des bois",     "Jacinthe des bois"),
   ("anemone-des-bois",      "l’anémone des bois",       "Anémone des bois"),
   ("muguet",                "le muguet",                "Muguet de mai"),
   ("perce-neige",           "le perce-neige",           "Perce-neige"),
   ("primevere",             "la primevère",             "Primevère commune"),
   ("digitale-pourpre",      "la digitale pourpre",      "Digitale pourpre"),
   ("ail-des-ours",          "l’ail des ours",           "Ail des ours"),
   ("violette-odorante",     "la violette",              "Violette odorante"),
   ("callune",               "la bruyère",               "Callune"),
  ],
 },
 3: {
  "faune": [
   ("bouquetin-alpes",       "le bouquetin",             "Bouquetin des Alpes"),
   ("chamois",               "le chamois",               "Chamois"),
   ("marmotte-alpine",       "la marmotte",              "Marmotte alpine"),
   ("aigle-royal",           "l’aigle royal",            "Aigle royal"),
   ("gypaete-barbu",         "le gypaète barbu",         "Gypaète barbu"),
   ("lievre-variable",       "le lièvre variable",       "Lièvre variable"),
   ("hermine",               "l’hermine",                "Hermine"),
   ("lagopede-alpin",        "le lagopède alpin",        "Lagopède alpin"),
   ("lynx-boreal",           "le lynx",                  "Lynx boréal"),
  ],
  "flore": [
   ("edelweiss",             "l’edelweiss",              "Edelweiss"),
   ("gentiane-acaule",       "la gentiane",              "Gentiane acaule"),
   ("rhododendron-ferrugineux", "le rhododendron",       "Rhododendron ferrugineux"),
   ("arnica-montagnes",      "l’arnica",                 "Arnica des montagnes"),
   ("crocus-printanier",     "le crocus",                "Crocus printanier"),
   ("pulsatille-alpes",      "la pulsatille",            "Pulsatille des Alpes"),
   ("lis-martagon",          "le lis martagon",          "Lis martagon"),
   ("soldanelle-alpes",      "la soldanelle",            "Soldanelle des Alpes"),
   ("trolle-europe",         "le trolle",                "Trolle d'Europe"),
  ],
 },
 4: {
  "faune": [
   ("vache",                 "la vache",                 "Vache"),
   ("mouton",                "le mouton",                "Mouton"),
   ("cheval",                "le cheval",                "Cheval"),
   ("cochon",                "le cochon",                "Cochon"),
   ("poule",                 "la poule",                 "Poule"),
   ("lievre-europe",         "le lièvre",                "Lièvre d'Europe"),
   ("cigogne-blanche",       "la cigogne blanche",       "Cigogne blanche"),
   ("hirondelle-rustique",   "l’hirondelle",             "Hirondelle rustique"),
   ("taupe-europe",          "la taupe",                 "Taupe d'Europe"),
  ],
  "flore": [
   ("coquelicot",            "le coquelicot",            "Coquelicot"),
   ("bleuet",                "le bleuet",                "Bleuet (plante)"),
   ("marguerite",            "la marguerite",            "Marguerite commune"),
   ("bouton-dor",            "le bouton-d’or",           "Renoncule âcre"),
   ("tournesol",             "le tournesol",             "Tournesol"),
   ("trefle-des-pres",       "le trèfle",                "Trèfle des prés"),
   ("colza",                 "le colza",                 "Colza"),
   ("mauve-sylvestre",       "la mauve",                 "Mauve sylvestre"),
   ("sauge-des-pres",        "la sauge des prés",        "Sauge des prés"),
  ],
 },
 5: {
  "faune": [
   ("dauphin-commun",        "le dauphin",               "Dauphin commun"),
   ("mouette-rieuse",        "la mouette rieuse",        "Mouette rieuse"),
   ("goeland-argente",       "le goéland argenté",       "Goéland argenté"),
   ("crabe-vert",            "le crabe",                 "Crabe vert"),
   ("etoile-de-mer",         "l’étoile de mer",          "Asterias rubens"),
   ("hippocampe",            "l’hippocampe",             "Hippocampe à museau court"),
   ("meduse-commune",        "la méduse",                "Aurelia aurita"),
   ("phoque-veau-marin",     "le phoque",                "Phoque veau-marin"),
   ("moule-commune",         "la moule",                 "Moule commune"),
  ],
  "flore": [
   ("oyat",                  "l’oyat",                   "Oyat"),
   ("panicaut-maritime",     "le chardon bleu des dunes", "Panicaut maritime"),
   ("criste-marine",         "la criste marine",         "Criste marine"),
   ("armerie-maritime",      "l’armérie maritime",       "Armérie maritime"),
   ("salicorne",             "la salicorne",             "Salicorne"),
   ("statice",               "la lavande de mer",        "Limonium"),
   ("liseron-des-dunes",     "le liseron des dunes",     "Liseron des dunes"),
   ("roquette-de-mer",       "la roquette de mer",       "Roquette de mer"),
   ("tamaris",               "le tamaris",               "Tamaris"),
  ],
 },
}

# Images imposées : quand l'illustration de l'article Wikipédia n'est pas une
# photographie exploitable pour un imagier (planche ancienne, gros plan
# illisible, animal noyé dans le décor). Renseigné après relecture des images.
OVERRIDES = {}


def entrees(periode=None):
    """Itère sur (periode, groupe, slug, nom, article)."""
    for p, groupes in sorted(IMAGIER.items()):
        if periode and p != periode:
            continue
        for groupe in ("faune", "flore"):
            for slug, nom, article in groupes[groupe]:
                yield p, groupe, slug, nom, article
