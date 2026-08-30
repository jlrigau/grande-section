# Contexte du dépôt

Matériel pédagogique pour une classe de **Grande Section** (année 2026-2027),
autour du projet annuel « À la découverte de la faune et de la flore » :
un milieu par période (ville, forêt, montagne, campagne, mer).

Tout est écrit **en français**, y compris les noms de fichiers, les
commentaires et les messages de commit.

## Organisation

| Chemin | Rôle |
|---|---|
| `01-…`, `02-…`, `03-progressions/`, `04-evaluations/` | les documents de l'enseignante, en Markdown |
| `site/` | l'application web (JS sans cadriciel), publiée sur GitHub Pages |
| `site/fiches/` | les fiches élève imprimables, une page A4 par fiche |
| `site/imagier/` | l'imagier Montessori, un cahier de cartes par période |
| `site/cartes-corpus/` | les cartes-corpus de vocabulaire, un cahier par période |
| `scripts/` | fabrication des pages et des images |
| `.claude/skills/` | les procédures outillées du dépôt (voir ci-dessous) |
| `referentiel/` | le programme sous forme de liste numérotée, et le contrôle de couverture |

Les PDF **ne sont pas versionnés** : `scripts/generer-pdf.sh` les fabrique à
chaque déploiement avec Chromium en mode `--print-to-pdf`.

Après avoir touché à un manifeste ou à un gabarit, régénérer les pages :

```sh
python3 scripts/generer-cartes-corpus.py # site/cartes-corpus/periode-N.html
python3 scripts/generer-imagier.py     # site/imagier/periode-N.html
python3 scripts/generer-credits.py     # page des crédits des fiches
```

Après avoir touché aux photographies de l'imagier, les contrôler :

```sh
python3 scripts/verifier-imagier.py    # espèce, crédits, cadrage, nombres annoncés ; code 1 s'il reste une anomalie
REVUE_DIR=/tmp python3 scripts/revoir-imagier.py   # les cartes telles qu'elles s'imprimeront
```

Et **finir par le PDF, jamais par le HTML** : la page d'un navigateur
s'allonge, une feuille A4 non. Les deux pires défauts de ce matériel — les
étiquettes non paginées qui s'imprimaient par-dessus les crédits, le pied de
la garde seul sur une page — n'existaient pas à l'écran. La marche à suivre
est dans le skill [`imagier-photos`](.claude/skills/imagier-photos/SKILL.md).

Après avoir touché à une progression, vérifier que l'année couvre toujours
le programme :

```sh
python3 scripts/couverture.py          # 159 attendus, sort en code 1 s'il en manque
```

`referentiel/cycle1-gs.yml` porte les attendus, un par ligne avec un
identifiant ; `referentiel/annotations-2026-2027.yml` dit ce que chaque
période traite. Une séance ajoutée sans accroche ne sera pas comptée.

**Ce fichier ne contient que des exigences du programme**, relues contre le
BO. Une règle que la classe se donne — le nombre d'espèces de l'imagier, par
exemple — n'y a pas sa place : logée parmi les autres, elle laisse croire que
le programme la prescrit, ce qui a déjà été affirmé à tort. Ces conventions
vivent dans le script du matériel concerné (ici `verifier-imagier.py`).

## Les skills du dépôt

| Skill | Quand |
|---|---|
| [`imagier-photos`](.claude/skills/imagier-photos/SKILL.md) | ajouter, remplacer ou vérifier une photographie de l'imagier — y compris quand la demande dit seulement « on ne voit pas bien l'animal » ou « change cette image » |
| [`fiches-illustrations`](.claude/skills/fiches-illustrations/SKILL.md) | ajouter, remplacer ou vérifier un pictogramme des fiches élève (`site/fiches/img/`) — y compris « le dessin de la poule est bizarre » ou « il me faut une image de tracteur » |

Un skill se mesure : `scripts/mesurer-declenchement.py` rejoue une liste de
demandes réalistes et regarde si le skill s'ouvre au bon moment (les cas de
l'imagier sont dans `tests/`). **Ne pas se fier au banc d'essai du
skill-creator** pour cela : il passe par un faux fichier de commande que
cette version de Claude Code n'expose pas comme un skill, si bien qu'aucune
demande ne déclenche jamais rien — il annonçait 10/20 là où la mesure
directe donne 20/20.

## Images : quelles sources, et laquelle éviter

### Wikimedia Commons — à éviter pour toute nouvelle moisson

`upload.wikimedia.org` limite très sévèrement l'adresse de sortie mutualisée
depuis laquelle tourne l'agent : au-delà de quelques fichiers, il répond
`429` avec un `Retry-After: 600`, soit **environ cinq images par tranche de
dix minutes**. Quatre-vingt-dix images demandent alors plusieurs heures — et
le seau de jetons est partagé, si bien que **le moindre `curl` de
vérification vers ce domaine relance le compteur**. Ni le parallélisme, ni le
regroupement des appels d'API, ni le passage par les fichiers d'origine
plutôt que les vignettes n'y changent quoi que ce soit : la limite porte sur
l'adresse, pas sur la manière de demander.

Les illustrations des fiches élève n'en dépendent plus : ce sont des
**pictogrammes** (Mulberry Symbols via jsDelivr, ARASAAC via son API — deux
sources sans bridage), versionnés dans `site/fiches/img/` avec leurs crédits.
La procédure complète — sources dans l'ordre, pièges des noms trompeurs,
planche de candidats obligatoire, installation, contrôles — est dans le
skill [`fiches-illustrations`](.claude/skills/fiches-illustrations/SKILL.md),
outillée par `scripts/chercher-pictos.py` (chercher / installer / verifier).
`scripts/chercher-images.py` et `scripts/images-manifest.py` sont l'ancienne
moisson Commons : ne pas les relancer.

### Vérifier la licence avant de retenir une image

Toute image entrant dans le dépôt doit porter une licence **compatible avec
un usage commercial** — CC0, CC BY ou CC BY-SA — parce que le matériel est
susceptible d'être diffusé au-delà du site gratuit. Une clause **NC** est
disqualifiante : les 26 pictogrammes ARASAAC des fiches sont dans ce cas et
restent à remplacer.

`scripts/pictos-libres.py` interroge le registre **Global Symbols**
(`globalsymbols.com`), qui fédère une trentaine de jeux de pictogrammes en
publiant la licence de chacun, et ne retient que les jeux libres — Mulberry
(le style de maison des fiches), OpenMoji, PiCom. Il retrouve ainsi 19 des
26 concepts ; les 7 autres sont à dessiner. Deux pièges : le registre cherche
en **sous-chaîne**, si bien que « lama » ramène *flamant* et « vague »
*microwave* — d'où le filtre sur le mot entier ; et Blissymbolics, bien que
libre, est un système d'écriture symbolique, inutilisable comme illustration.

### iNaturalist — la source des photographies d'espèces

`scripts/chercher-images-imagier.py` interroge
`https://api.inaturalist.org/v1/observations`. Aucune limitation gênante :
les cent quatre-vingts photographies de l'imagier sont fabriquées en quelques
minutes. Les paramètres qui comptent :

- `taxon_name` — **toujours le nom scientifique** (`Quercus robur`, et non
  « chêne ») ; c'est pourquoi `scripts/imagier-manifest.py` porte le taxon de
  chaque espèce. Une recherche par nom vernaculaire est bien moins fiable.
- `quality_grade=research` — l'espèce a été confirmée par plusieurs
  naturalistes. À relâcher pour les animaux domestiques (vache, poule,
  cochon), qui n'ont jamais d'observation de « qualité recherche »
  puisqu'ils ne sont pas sauvages : le script le fait tout seul.
- `photo_license=cc0,cc-by,cc-by-sa` — les seules licences qui autorisent la
  publication sur le site avec mention de l'auteur.
- `original_dimensions` — filtrer en deçà de 1000 px de côté, une photo plus
  petite ne s'imprime pas proprement sur une carte.

Les fichiers sont servis par deux hôtes
(`inaturalist-open-data.s3.amazonaws.com` et `static.inaturalist.org`) et
sous plusieurs extensions ; `url_photo()` les essaie tous. Chaque source est
gardée en cache dans `/tmp/imagier-source`, ce qui permet de **rejouer un
recadrage sans réseau** (`RECADRER=1`).

### Choisir une photographie de carte : voir le skill

La procédure complète — planches de candidats, critères de sélection,
paramètres d'iNaturalist, contrôle avant publication — est dans le skill
[`imagier-photos`](.claude/skills/imagier-photos/SKILL.md), à charger avant
de toucher aux images de l'imagier. L'essentiel, en bref :

**Aucun tri automatique ne convient.** `order_by=votes` met en avant les
photographies les plus *aimées*, spectaculaires plutôt qu'illustratives : un
ours mangeant des pissenlits pour « le pissenlit », un renard argenté pour
« le renard roux ». Chaque photographie se choisit à l'œil, sur une planche
de candidats, et son identifiant s'inscrit dans `OVERRIDES`
(`scripts/imagier-manifest.py`).

**Cinq critères**, tous nés d'une carte qu'il a fallu refaire : un seul
individu ; une image qui convient à des enfants de cinq ans (le vivier est
plein de saillies, de prédation et de crânes) ; l'animal entier, de face ou
de profil ; une image qui remplit la carte ; rien autour du sujet.

**Deux pièges qui donnent la mauvaise espèce.** Chercher par `taxon_id`,
jamais par `taxon_name` : ce dernier accroche les noms vernaculaires et a
fait publier un blaireau d'Amérique pour « le blaireau », un rhebok
d'Afrique du Sud pour « le chevreuil », une marmotte d'Amérique pour « la
marmotte ». Et les animaux de la ferme se cherchent avec `captive=true`,
faute de quoi le cochon d'élevage devient un sanglier féral. Même avec
`taxon_id`, le vivier contient des espèces voisines : les planches les
encadrent en rouge, et `scripts/verifier-imagier.py` refuse de laisser
passer une carte mal identifiée.

### Faune **et flore**

La flore ne se réduit pas aux fleurs : elle comprend les arbres, les
arbustes, les fougères, les mousses, les graminées, les algues et les
cultures. Chaque période compte dix-huit espèces de faune et dix-huit de
flore, et
cette dernière liste doit rester variée — un milieu représenté par neuf
fleurs serait faux.
