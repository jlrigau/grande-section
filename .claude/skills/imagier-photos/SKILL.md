---
name: imagier-photos
description: Choisir, fabriquer et vérifier les photographies des cartes de nomenclature de l'imagier Montessori faune et flore (site/imagier/). À utiliser dès qu'il faut ajouter une espèce, remplacer une image jugée mauvaise, refaire une carte ou une période entière, ou toucher à scripts/imagier-manifest.py, scripts/chercher-images-imagier.py, scripts/candidats-imagier.py et scripts/verifier-imagier.py. Se déclenche aussi quand la demande ne nomme aucun fichier : « on ne voit pas bien la taupe », « il y a deux animaux sur la carte », « cette photo est trop chargée », « change l'image du hérisson », « refais les images de la période 3 », « il manque le blaireau ». Charger ce skill AVANT de télécharger la moindre image : les pièges décrits ici ont déjà fait publier cinq cartes montrant la mauvaise espèce.
---

# Les photographies de l'imagier

L'imagier est un jeu de cartes de nomenclature Montessori : cinq cahiers A4,
un par période et par milieu, trente-six espèces chacun — dix-huit de faune,
dix-huit de flore. Chaque espèce donne trois cartes : photo + nom, photo seule,
nom seul. Les enfants ont cinq ans et **ne savent pas encore lire** : la
photographie porte seule le sens. Une image ambiguë ne fait pas une carte
médiocre, elle fait une carte fausse.

Les images vivent dans `site/imagier/img/`, en 1100 × 753 px (environ 300 dpi
sur la zone photo des cartes), avec `credits.json` pour l'auteur et la
licence de chacune.

## Les cinq critères d'une bonne carte

Chacun vient d'une carte qu'il a fallu refaire. Les garder en tête pendant
la sélection évite d'y revenir.

1. **Un seul individu.** Deux chevreuils, deux renards qui se battent, une
   poule au milieu de ses poussins, une moule dans une main : l'enfant ne
   sait pas lequel on nomme. Un autre animal au second plan compte aussi —
   le cheval qui portait un héron garde-bœufs sur le dos a été écarté.
2. **Une image qui convient à des enfants de cinq ans.** Ni saillie, ni
   prédation, ni animal mort, ni crâne. Le vivier d'iNaturalist en est plein
   pour le blaireau, le cochon et le renard : c'est même ce que le tri par
   popularité remonte en premier.
3. **L'animal entier, de face ou de profil.** La taupe vue de dessus n'était
   qu'une masse noire ; de trois quarts, on lui voit le museau pointu et la
   patte-pelle, et elle redevient nommable. Un portrait de tête passe quand
   le trait distinctif y est (les cornes du bouquetin), mais l'animal entier
   vaut mieux.
4. **L'image remplit la carte.** Le recadrage s'en charge et ne laisse plus
   jamais de bande blanche, mais un cliché en hauteur perd beaucoup à la
   coupe : à qualité égale, préférer une photographie en largeur.
5. **Rien autour du sujet.** Le pigeon photographié dans une galerie
   marchande se perdait dans les vitrines. Fond simple, sujet occupant le
   cadre. Pour la flore, viser la plante entière ou l'organe qui l'identifie :
   la feuille palmée et la « bougie » du marronnier, l'écorce blanche du
   bouleau, la feuille piquante et les baies du houx, l'épi du blé.

## La boucle de travail

Quatre étapes, toujours dans cet ordre. Ne jamais sauter la planche de
candidats : **aucun tri automatique ne convient à un imagier** (voir plus
bas), et une image choisie sans être regardée est une image à refaire.

```sh
# 1 — regarder ce qui existe : huit candidates par espèce, numérotées
CANDIDATS_DIR=/tmp/cand python3 scripts/candidats-imagier.py taupe-europe cochon
#    (aussi : « 3-faune », « 5-flore » pour une planche entière ; sans
#     argument, les dix planches)
#    Vivier pauvre — troupeaux et zébus pour « la vache », rosettes
#    hivernales pour « la digitale » ? L'élargir plutôt que se rabattre :
PLACE=97391 MOIS=5,6,7 PAGES=4 NB_CANDIDATS=12 \
  CANDIDATS_DIR=/tmp/cand python3 scripts/candidats-imagier.py digitale

# 2 — départager deux clichés proches, en grand ; CADRE=1 les montre tels
#     que la carte les rognera, ce qui départage souvent à soi seul
CADRE=1 python3 scripts/zoom-imagier.py /tmp/zoom.jpg 291736892 114935359

# 3 — inscrire le choix dans OVERRIDES de scripts/imagier-manifest.py,
#     puis fabriquer l'image
FORCE=1 python3 scripts/chercher-images-imagier.py taupe-europe cochon

# 4 — contrôler : espèce, crédits, cadrage
python3 scripts/verifier-imagier.py
```

Puis regarder le résultat tel qu'il s'imprimera, ce que le contrôle
automatique ne sait pas faire :

```sh
REVUE_DIR=/tmp python3 scripts/revoir-imagier.py 4
```

Enfin, si le manifeste a changé, régénérer les pages :

```sh
python3 scripts/generer-imagier.py
```

Les PDF ne sont pas versionnés : `scripts/generer-pdf.sh` les refabrique au
déploiement.

## Les pièges d'iNaturalist

La source est `https://api.inaturalist.org/v1/observations`, sans limitation
gênante — les cent quatre-vingts photographies se fabriquent en quelques
minutes. Trois pièges, tous vérifiés à leurs dépens :

**Chercher par `taxon_id`, jamais par `taxon_name`.** Le paramètre
`taxon_name` accroche aussi les noms vernaculaires et rend des espèces d'un
autre continent : `Meles meles` ramenait le blaireau d'Amérique
(*Taxidea taxus*), `Capreolus capreolus` un rhebok d'Afrique du Sud
(*Pelea capreolus*), `Marmota marmota` une marmotte d'Amérique. Cinq cartes
fausses sont passées ainsi. Les scripts résolvent désormais le nom en
identifiant de taxon ; il reste que le vivier contient des espèces voisines,
que les planches encadrent en rouge — **ne pas choisir une vignette
encadrée de rouge**.

**Les animaux de la ferme se cherchent avec `captive=true`.** Sans ce
filtre, iNaturalist ne remonte que des populations retournées à l'état
féral : des cochons impossibles à distinguer d'un sanglier, des poules de
rue. Les espèces concernées sont listées dans `DOMESTIQUES`
(`scripts/imagier-manifest.py`).

**Le classement par popularité met en avant le spectaculaire, pas
l'illustratif** : un ours mangeant des pissenlits pour « le pissenlit », un
renard argenté pour « le renard roux », un bourgeon en gros plan pour « le
marronnier ». C'est la raison d'être des planches de candidats.

**Pour une plante, penser à la saison.** Le tri par votes remonte volontiers
des rosettes de feuilles hivernales ou des pieds défleuris : la digitale
n'était qu'une touffe verte sur les quarante premières candidates. `MOIS=5,6,7`
(les mois de floraison de l'espèce) fait apparaître un vrai éventail. Même
remarque pour les arbres : la feuille, la fleur et le fruit ne se
photographient pas au même moment.

Le script ne garde déjà qu'**un cliché par observateur** — sans quoi
quarante candidates sont parfois quarante photos du même pied, prises le
même jour par la même personne.

Quand une espèce résiste, deux filtres sauvent souvent la mise :
`place_id=97391` (l'Europe), qui écarte les espèces voisines d'autres
continents, et `captive=true`, qui rend les animaux de parcs animaliers,
photographiés en plein jour. Le détail des paramètres est dans
[references/inaturalist.md](references/inaturalist.md).

## Ne pas aller sur Wikimedia Commons

`upload.wikimedia.org` limite l'adresse de sortie mutualisée à environ cinq
fichiers par tranche de dix minutes (`429` avec `Retry-After: 600`), et
l'API `commons.wikimedia.org` finit par répondre `429` elle aussi. Une
moisson de l'imagier entier y prendrait des jours. Ni le parallélisme,
ni le regroupement des appels n'y changent rien : la limite porte sur
l'adresse. Le moindre `curl` de vérification relance le compteur.

## Licences

Seules CC0, CC BY et CC BY-SA sont acceptées : le matériel est susceptible
d'être diffusé au-delà du site gratuit, donc **une clause NC est
disqualifiante**. L'auteur et la licence sont obligatoires — le script de
moisson refuse une photographie dont il ne retrouve pas les crédits, et
`verifier-imagier.py` le contrôle avant publication.

## Ajouter une espèce

Ajouter le triplet `(slug, nom, taxon)` dans `IMAGIER` de
`scripts/imagier-manifest.py`, avec le **nom scientifique** — la recherche
par nom vernaculaire est bien moins fiable. Le `nom` est ce qui s'écrit sur
l'étiquette, article compris (« le hérisson »). Puis dérouler la boucle
ci-dessus.

La flore ne se réduit pas aux fleurs : elle comprend arbres, arbustes,
fougères, mousses, graminées, algues et cultures, et chaque période doit
rester variée — un milieu représenté par neuf fleurs serait faux.
