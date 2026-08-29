# -*- coding: utf-8 -*-
"""Manifeste de l'imagier Montessori « faune et flore ».

Pour chaque période (milieu) : 9 espèces de faune et 9 espèces de flore.
La flore, ce n'est pas seulement les fleurs : on y trouve les arbres, les
arbustes, les fougères, les mousses, les graminées, les algues et les
plantes cultivées, choisis pour être caractéristiques du milieu et
observables lors des sorties.

Chaque entrée décrit :
  slug   — nom de fichier de l'image (sans extension) ;
  nom    — le mot écrit sur l'étiquette (script, minuscules) ;
  taxon  — le nom scientifique, qui sert à interroger iNaturalist.

Utilisé par scripts/chercher-images-imagier.py (photographies + crédits)
et par scripts/generer-imagier.py (génération des planches HTML).
"""

MILIEUX = [
    (1, "ville",    "🏙️", "La ville",    "Les animaux et les plantes de la ville, des parcs et des trottoirs."),
    (2, "foret",    "🌳", "La forêt",    "Les animaux et les plantes des bois et des sous-bois."),
    (3, "montagne", "⛰️", "La montagne", "Les animaux et les plantes de l’étage montagnard et alpin."),
    (4, "campagne", "🌾", "La campagne", "Les animaux de la ferme et des prés, les cultures et les fleurs des champs."),
    (5, "mer",      "🌊", "La mer",      "Les animaux du bord de mer, les plantes du littoral et les algues."),
]

IMAGIER = {
 1: {
  "faune": [
   ("pigeon-biset",          "le pigeon biset",          "Columba livia"),
   ("moineau-domestique",    "le moineau domestique",    "Passer domesticus"),
   ("merle-noir",            "le merle noir",            "Turdus merula"),
   ("mesange-charbonniere",  "la mésange charbonnière",  "Parus major"),
   ("martinet-noir",         "le martinet noir",         "Apus apus"),
   ("herisson-europe",       "le hérisson",              "Erinaceus europaeus"),
   ("ecureuil-roux",         "l’écureuil roux",          "Sciurus vulgaris"),
   ("coccinelle-7-points",   "la coccinelle",            "Coccinella septempunctata"),
   ("abeille-domestique",    "l’abeille",                "Apis mellifera"),
  ],
  "flore": [
   ("platane",               "le platane",               "Platanus x hispanica"),
   ("marronnier",            "le marronnier",            "Aesculus hippocastanum"),
   ("tilleul",               "le tilleul",               "Tilia platyphyllos"),
   ("lierre",                "le lierre",                "Hedera helix"),
   ("mousse-trottoir",       "la mousse",                "Bryum argenteum"),
   ("paquerette",            "la pâquerette",            "Bellis perennis"),
   ("pissenlit",             "le pissenlit",             "Taraxacum officinale"),
   ("rose-tremiere",         "la rose trémière",         "Alcea rosea"),
   ("geranium-balcon",       "le géranium",              "Pelargonium zonale"),
  ],
 },
 2: {
  "faune": [
   ("cerf-elaphe",           "le cerf",                  "Cervus elaphus"),
   ("chevreuil",             "le chevreuil",             "Capreolus capreolus"),
   ("sanglier",              "le sanglier",              "Sus scrofa"),
   ("renard-roux",           "le renard roux",           "Vulpes vulpes"),
   ("blaireau-europeen",     "le blaireau",              "Meles meles"),
   ("chouette-hulotte",      "la chouette hulotte",      "Strix aluco"),
   ("pic-vert",              "le pic vert",              "Picus viridis"),
   ("salamandre-tachetee",   "la salamandre",            "Salamandra salamandra"),
   ("fourmi-rousse",         "la fourmi rousse",         "Formica rufa"),
  ],
  "flore": [
   ("chene",                 "le chêne",                 "Quercus robur"),
   ("hetre",                 "le hêtre",                 "Fagus sylvatica"),
   ("sapin-blanc",           "le sapin",                 "Abies alba"),
   ("bouleau",               "le bouleau",               "Betula pendula"),
   ("houx",                  "le houx",                  "Ilex aquifolium"),
   ("fougere-aigle",         "la fougère",               "Pteridium aquilinum"),
   ("ronce",                 "la ronce",                 "Rubus fruticosus"),
   ("jacinthe-des-bois",     "la jacinthe des bois",     "Hyacinthoides non-scripta"),
   ("muguet",                "le muguet",                "Convallaria majalis"),
  ],
 },
 3: {
  "faune": [
   ("bouquetin-alpes",       "le bouquetin",             "Capra ibex"),
   ("chamois",               "le chamois",               "Rupicapra rupicapra"),
   ("marmotte-alpine",       "la marmotte",              "Marmota marmota"),
   ("aigle-royal",           "l’aigle royal",            "Aquila chrysaetos"),
   ("gypaete-barbu",         "le gypaète barbu",         "Gypaetus barbatus"),
   ("lievre-variable",       "le lièvre variable",       "Lepus timidus"),
   ("hermine",               "l’hermine",                "Mustela erminea"),
   ("lagopede-alpin",        "le lagopède",              "Lagopus muta"),
   ("lynx-boreal",           "le lynx",                  "Lynx lynx"),
  ],
  "flore": [
   ("epicea",                "l’épicéa",                 "Picea abies"),
   ("meleze",                "le mélèze",                "Larix decidua"),
   ("pin-cembro",            "l’arolle",                 "Pinus cembra"),
   ("rhododendron-ferrugineux", "le rhododendron",       "Rhododendron ferrugineum"),
   ("myrtille",              "la myrtille",              "Vaccinium myrtillus"),
   ("gentiane-acaule",       "la gentiane",              "Gentiana acaulis"),
   ("edelweiss",             "l’edelweiss",              "Leontopodium nivale"),
   ("arnica-montagnes",      "l’arnica",                 "Arnica montana"),
   ("joubarbe",              "la joubarbe",              "Sempervivum montanum"),
  ],
 },
 4: {
  "faune": [
   ("vache",                 "la vache",                 "Bos taurus"),
   ("mouton",                "le mouton",                "Ovis aries"),
   ("cheval",                "le cheval",                "Equus caballus"),
   ("cochon",                "le cochon",                "Sus scrofa domesticus"),
   ("poule",                 "la poule",                 "Gallus gallus domesticus"),
   ("lievre-europe",         "le lièvre",                "Lepus europaeus"),
   ("cigogne-blanche",       "la cigogne blanche",       "Ciconia ciconia"),
   ("hirondelle-rustique",   "l’hirondelle",             "Hirundo rustica"),
   ("taupe-europe",          "la taupe",                 "Talpa europaea"),
  ],
  "flore": [
   ("ble",                   "le blé",                   "Triticum aestivum"),
   ("mais",                  "le maïs",                  "Zea mays"),
   ("tournesol",             "le tournesol",             "Helianthus annuus"),
   ("colza",                 "le colza",                 "Brassica napus"),
   ("pommier",               "le pommier",               "Malus domestica"),
   ("coquelicot",            "le coquelicot",            "Papaver rhoeas"),
   ("bleuet",                "le bleuet",                "Centaurea cyanus"),
   ("trefle-des-pres",       "le trèfle",                "Trifolium pratense"),
   ("ortie",                 "l’ortie",                  "Urtica dioica"),
  ],
 },
 5: {
  "faune": [
   ("dauphin-commun",        "le dauphin",               "Delphinus delphis"),
   ("mouette-rieuse",        "la mouette rieuse",        "Chroicocephalus ridibundus"),
   ("goeland-argente",       "le goéland argenté",       "Larus argentatus"),
   ("crabe-vert",            "le crabe",                 "Carcinus maenas"),
   ("etoile-de-mer",         "l’étoile de mer",          "Asterias rubens"),
   ("hippocampe",            "l’hippocampe",             "Hippocampus hippocampus"),
   ("meduse-commune",        "la méduse",                "Aurelia aurita"),
   ("phoque-veau-marin",     "le phoque",                "Phoca vitulina"),
   ("moule-commune",         "la moule",                 "Mytilus edulis"),
  ],
  "flore": [
   ("pin-maritime",          "le pin maritime",          "Pinus pinaster"),
   ("tamaris",               "le tamaris",               "Tamarix gallica"),
   ("oyat",                  "l’oyat",                   "Ammophila arenaria"),
   ("panicaut-maritime",     "le chardon des dunes",     "Eryngium maritimum"),
   ("criste-marine",         "la criste marine",         "Crithmum maritimum"),
   ("salicorne",             "la salicorne",             "Salicornia europaea"),
   ("armerie-maritime",      "l’armérie",                "Armeria maritima"),
   ("fucus",                 "le goémon",                "Fucus vesiculosus"),
   ("laitue-de-mer",         "la laitue de mer",         "Ulva lactuca"),
  ],
 },
}

# Photographies imposées : identifiant d'une photo iNaturalist, quand celle
# retenue automatiquement ne montre pas bien l'espèce. Renseigné après
# relecture des planches contact.
OVERRIDES = {
    "abeille-domestique": 355572665,
    "aigle-royal": 631265943,
    "armerie-maritime": 114215839,
    "arnica-montagnes": 466384214,
    "blaireau-europeen": 26272878,
    "ble": 113479543,
    "bleuet": 403564813,
    "bouleau": 71735669,
    "bouquetin-alpes": 602532351,
    "cerf-elaphe": 103763755,
    "chamois": 398736721,
    "chene": 467469040,
    "cheval": 46190755,
    "chevreuil": 133321087,
    "chouette-hulotte": 120601572,
    "cigogne-blanche": 601229857,
    "coccinelle-7-points": 97384573,
    "cochon": 347459056,
    "colza": 113010818,
    "coquelicot": 114734674,
    "crabe-vert": 451212512,
    "criste-marine": 405045340,
    "dauphin-commun": 701008453,
    "ecureuil-roux": 357280857,
    "edelweiss": 560454686,
    "epicea": 72268912,
    "etoile-de-mer": 261432691,
    "fougere-aigle": 345054962,
    "fourmi-rousse": 134421569,
    "fucus": 96840209,
    "gentiane-acaule": 22163700,
    "geranium-balcon": 241370288,
    "goeland-argente": 284617710,
    "gypaete-barbu": 364202175,
    "herisson-europe": 79670738,
    "hermine": 489011064,
    "hetre": 274002483,
    "hippocampe": 364753654,
    "hirondelle-rustique": 635249563,
    "houx": 448317645,
    "jacinthe-des-bois": 359325185,
    "joubarbe": 90509238,
    "lagopede-alpin": 20086213,
    "laitue-de-mer": 266271508,
    "lierre": 38428455,
    "lievre-europe": 135144932,
    "lievre-variable": 2887757,
    "lynx-boreal": 246545089,
    "mais": 506123111,
    "marmotte-alpine": 3424124,
    "marronnier": 73427333,
    "martinet-noir": 92256731,
    "meduse-commune": 649274082,
    "meleze": 56039131,
    "merle-noir": 186757278,
    "mesange-charbonniere": 248486851,
    "moineau-domestique": 136543105,
    "mouette-rieuse": 675350279,
    "moule-commune": 3904219,
    "mousse-trottoir": 94133993,
    "mouton": 632127409,
    "muguet": 196688665,
    "myrtille": 670186992,
    "ortie": 26527149,
    "oyat": 208072203,
    "panicaut-maritime": 75688147,
    "paquerette": 488466115,
    "phoque-veau-marin": 331671523,
    "pic-vert": 255640895,
    "pigeon-biset": 613429468,
    "pin-cembro": 445512561,
    "pin-maritime": 700093064,
    "pissenlit": 270994499,
    "platane": 55263068,
    "pommier": 491893168,
    "poule": 255590439,
    "renard-roux": 237607564,
    "rhododendron-ferrugineux": 139065781,
    "ronce": 419308619,
    "rose-tremiere": 272214329,
    "salamandre-tachetee": 61491535,
    "salicorne": 50768950,
    "sanglier": 34825790,
    "sapin-blanc": 180560003,
    "tamaris": 404514988,
    "taupe-europe": 653771496,
    "tilleul": 533980541,
    "tournesol": 155296308,
    "trefle-des-pres": 134044,
    "vache": 29102489,
}


def entrees(periode=None):
    """Itère sur (periode, groupe, slug, nom, taxon)."""
    for p, groupes in sorted(IMAGIER.items()):
        if periode and p != periode:
            continue
        for groupe in ("faune", "flore"):
            for slug, nom, taxon in groupes[groupe]:
                yield p, groupe, slug, nom, taxon
