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
| `scripts/` | fabrication des pages et des images |
| `referentiel/` | le programme sous forme de liste numérotée, et le contrôle de couverture |

Les PDF **ne sont pas versionnés** : `scripts/generer-pdf.sh` les fabrique à
chaque déploiement avec Chromium en mode `--print-to-pdf`.

Après avoir touché à un manifeste ou à un gabarit, régénérer les pages :

```sh
python3 scripts/generer-imagier.py     # site/imagier/periode-N.html
python3 scripts/generer-credits.py     # page des crédits des fiches
```

Après avoir touché aux photographies de l'imagier, les contrôler :

```sh
python3 scripts/verifier-imagier.py    # espèce, crédits, cadrage ; code 1 s'il reste une anomalie
```

Après avoir touché à une progression, vérifier que l'année couvre toujours
le programme :

```sh
python3 scripts/couverture.py          # 159 attendus, sort en code 1 s'il en manque
```

`referentiel/cycle1-gs.yml` porte les attendus, un par ligne avec un
identifiant ; `referentiel/annotations-2026-2027.yml` dit ce que chaque
période traite. Une séance ajoutée sans accroche ne sera pas comptée.

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

`scripts/chercher-images.py` et `scripts/images-manifest.py` s'en servent
encore pour les **dessins** des fiches élève. Ces images-là sont déjà
téléchargées et versionnées dans `site/fiches/img/` : le script n'a pas à
être relancé. S'il faut de nouveaux dessins, ne pas compter sur Commons —
chercher d'abord ailleurs (Openclipart, Pixabay, ou un dessin fabriqué en
SVG), et n'y revenir qu'en dernier recours, pour une poignée de fichiers.

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
les quatre-vingt-dix photographies de l'imagier sont fabriquées en quelques
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

### Le classement automatique ne convient pas à un imagier

`order_by=votes` met en avant les photographies les plus **aimées**, qui sont
spectaculaires plutôt qu'illustratives : un ours en train de manger des
pissenlits pour « le pissenlit », un renard **argenté** pour « le renard
roux », un bourgeon en gros plan pour « le marronnier ». `order_by=…
identification_agreements` fait pire encore. Il n'existe pas de tri
automatique satisfaisant.

La méthode qui marche, et qu'il faut reprendre pour toute nouvelle espèce :

```sh
CANDIDATS_DIR=/tmp/cand python3 scripts/candidats-imagier.py 3-faune
```

Le script assemble une planche numérotée de cinq candidates par espèce ; on
la regarde, on retient celle où la plante ou l'animal est **le sujet, entier
et reconnaissable à distance**, et on inscrit l'identifiant de la
photographie dans le dictionnaire `OVERRIDES` de
`scripts/imagier-manifest.py`. Les quatre-vingt-dix photographies actuelles
ont toutes été choisies ainsi.

### Ce qui fait une bonne photographie de carte

Une carte de nomenclature n'est pas une belle image : c'est une image dont un
enfant de cinq ans tire le nom sans hésiter. Cinq règles, toutes issues de
cartes qu'il a fallu refaire :

1. **Un seul individu.** Deux chevreuils, deux renards qui se battent, une
   poule et ses poussins : l'enfant ne sait plus lequel on nomme.
2. **Une image de son âge.** Pas de saillie, pas de prédation, pas d'animal
   mort ni de crâne — le vivier d'iNaturalist en est plein pour le blaireau
   et le cochon.
3. **L'animal entier, de face ou de profil.** La taupe vue de dessus n'était
   qu'une masse noire ; de trois quarts, on lui voit le museau pointu et la
   patte-pelle, et elle devient reconnaissable.
4. **L'image remplit la carte.** Le recadrage est fait pour cela et ne laisse
   plus jamais de bande blanche ; il reste qu'un cliché en hauteur perd
   beaucoup à la coupe, d'où la préférence donnée aux photographies en
   largeur.
5. **Rien autour.** Le pigeon photographié dans une galerie marchande se
   perdait dans les vitrines. Le sujet doit occuper le cadre, sur un fond
   simple.

Ces règles valent aussi pour la flore : la plante entière ou l'organe qui
l'identifie — la feuille palmée et la « bougie » du marronnier, l'écorce
blanche du bouleau, la feuille piquante et les baies du houx.

### Deux pièges d'iNaturalist qui donnent la mauvaise espèce

**Chercher par `taxon_id`, jamais par `taxon_name`.** Le paramètre
`taxon_name` accroche aussi les noms vernaculaires et rend des espèces d'un
autre continent : `Meles meles` ramenait le **blaireau d'Amérique**
(*Taxidea taxus*) et `Capreolus capreolus` un **rhebok d'Afrique du Sud**
(*Pelea capreolus*) — deux cartes fausses passées inaperçues. Les scripts
résolvent donc le nom scientifique en identifiant de taxon (`/v1/taxa`), en
exigeant le nom exact, ou à défaut le terme sur lequel iNaturalist a
accroché, ce qui rattrape les renommages (`Ammophila arenaria` est devenu
`Calamagrostis arenaria`). Pour contrôler après coup, comparer le taxon de
chaque observation créditée à celui du manifeste.

**Les animaux de la ferme se cherchent avec `captive=true`.** Sans ce
filtre, iNaturalist ne remonte que des populations retournées à l'état
féral : des cochons impossibles à distinguer d'un sanglier, des poules de
rue. Le manifeste liste ces espèces dans `DOMESTIQUES`.

Quand une espèce reste introuvable dans de bonnes conditions, deux filtres
sauvent souvent la mise : `place_id=97391` (l'Europe), qui écarte les
espèces voisines d'autres continents, et `captive=true`, qui rend les
animaux de parcs animaliers, photographiés en plein jour.

### Faune **et flore**

La flore ne se réduit pas aux fleurs : elle comprend les arbres, les
arbustes, les fougères, les mousses, les graminées, les algues et les
cultures. Chaque période compte neuf espèces de faune et neuf de flore, et
cette dernière liste doit rester variée — un milieu représenté par neuf
fleurs serait faux.
