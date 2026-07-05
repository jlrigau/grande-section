# Grande Section — Année 2026-2027

> 📖 **Consulter en ligne** : [jlrigau.github.io/grande-section](https://jlrigau.github.io/grande-section/)

## Projet annuel : « À la découverte de la faune et de la flore »

Ce dépôt contient l'ensemble du matériel de préparation pour une classe de **Grande Section de maternelle** pour l'année scolaire **2026-2027**, conforme au **programme du cycle 1 (2024-2026, BO n°19 du 7 mai 2026 et BO n°41 du 31 octobre 2024)**, y compris le programme d'**éducation à la vie affective et relationnelle (EVAR)**.

L'année est organisée autour de cinq milieux, un par période :

| Période | Thème | Dates indicatives |
|---|---|---|
| **Période 1** | 🏙️ La ville | 1er septembre → 16 octobre 2026 (7 semaines) |
| **Période 2** | 🌳 La forêt | 2 novembre → 18 décembre 2026 (7 semaines) |
| **Période 3** | ⛰️ La montagne | 4 janvier → vacances d'hiver 2027 (5 à 7 semaines selon zone) |
| **Période 4** | 🌾 La campagne | retour des vacances d'hiver → vacances de printemps (≈ 6 semaines) |
| **Période 5** | 🌊 La mer | retour des vacances de printemps → 2 juillet 2027 (9 à 11 semaines selon zone) |

## Calendrier selon votre zone de vacances

> **Sur le [site en ligne](https://jlrigau.github.io/grande-section/)**, sélectionnez votre zone de vacances (A, B ou C) en haut de page : le calendrier ci-dessous et les dates de toutes les périodes, dans toutes les progressions et évaluations, s'adaptent automatiquement. Les dates proviennent du jeu de données officiel [fr-en-calendrier-scolaire](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/) (open data du ministère).

<p id="zone-hint" class="zone-hint"></p>
<div id="calendrier-zones">

| Vacances 2026-2027 | Zone A | Zone B | Zone C |
|---|---|---|---|
| Toussaint | 17 oct. → 1er nov. 2026 | idem | idem |
| Noël | 19 déc. 2026 → 3 janv. 2027 | idem | idem |
| Hiver | 13 févr. → 28 févr. 2027 | 20 févr. → 7 mars 2027 | 6 févr. → 21 févr. 2027 |
| Printemps | 10 avr. → 25 avr. 2027 | 17 avr. → 2 mai 2027 | 3 avr. → 18 avr. 2027 |
| Été | à partir du 3 juillet 2027 | idem | idem |

</div>

## Contenu du dépôt

### 1. Pilotage de l'année
- [`01-projet-annuel.md`](01-projet-annuel.md) — présentation du projet, fils rouges, sorties, corpus de vocabulaire (3 par période), bibliographie d'albums, chants et œuvres par période.
- [`02-programmation-annuelle.md`](02-programmation-annuelle.md) — **programmation** synthétique : tous les domaines × les 5 périodes (le « quoi, quand »).

### 2. Progressions par domaine (le « comment, dans quel ordre »)
- [`03-progressions/01-langage-oral-ecrit.md`](03-progressions/01-langage-oral-ecrit.md) — développement et structuration du langage oral et écrit.
- [`03-progressions/02-mathematiques.md`](03-progressions/02-mathematiques.md) — acquisition des premiers outils mathématiques.
- [`03-progressions/03-activites-physiques.md`](03-progressions/03-activites-physiques.md) — agir, s'exprimer, comprendre à travers les activités physiques.
- [`03-progressions/04-activites-artistiques.md`](03-progressions/04-activites-artistiques.md) — agir, s'exprimer, comprendre à travers les activités artistiques.
- [`03-progressions/05-temps-espace.md`](03-progressions/05-temps-espace.md) — se repérer dans le temps et l'espace.
- [`03-progressions/06-monde-vivant-matiere-objets.md`](03-progressions/06-monde-vivant-matiere-objets.md) — découvrir le monde du vivant, de la matière et des objets.
- [`03-progressions/07-evar.md`](03-progressions/07-evar.md) — éducation à la vie affective et relationnelle (3 séances spécifiques obligatoires).

### 3. Site en ligne, fiches élève et PDF
- `site/` — l'application web (navigation, sélecteur de zone A/B/C, téléchargement des PDF).
- `site/fiches/` — les **fiches élève** imprimables (une page A4 par fiche, consigne donnée à l'oral par l'enseignante), un cahier par période.
- `scripts/generer-pdf.sh` — génération automatique, à chaque déploiement, de tous les PDF : chaque document dans chaque zone (`pdf/zone-A|B|C/…`) + les 5 cahiers de fiches élève (`pdf/fiches-eleve-periode-N.pdf`).

### 4. Fiches d'évaluation (une batterie par période, adaptée au thème)
- [`04-evaluations/00-mode-emploi-et-livret-de-suivi.md`](04-evaluations/00-mode-emploi-et-livret-de-suivi.md) — principes d'évaluation positive, codage, grille de suivi annuelle.
- [`04-evaluations/periode-1-ville.md`](04-evaluations/periode-1-ville.md)
- [`04-evaluations/periode-2-foret.md`](04-evaluations/periode-2-foret.md)
- [`04-evaluations/periode-3-montagne.md`](04-evaluations/periode-3-montagne.md)
- [`04-evaluations/periode-4-campagne.md`](04-evaluations/periode-4-campagne.md)
- [`04-evaluations/periode-5-mer.md`](04-evaluations/periode-5-mer.md)

## Rappels structurants du programme (GS)

- **Vocabulaire** : enseignement explicite de **3 corpus de mots par période** ; mémorisation évaluée chaque mois et chaque période ; ≈ 2 500 mots maîtrisés en fin de GS.
- **Un texte mémorisé par semaine** (comptine, chant, poésie, extrait d'album) ; **au moins 10 comptines ou chants** dans l'année, en réinvestissant ceux des années précédentes ; **au moins 3 œuvres musicales patrimoniales** connues.
- **Éducation physique quotidienne** (30 à 45 minutes effectives), unités d'apprentissage de **6 à 8 séances minimum**, couvrant les 4 sous-domaines.
- **Écriture** : entraînement structuré de l'écriture **cursive**, encodage de mots transparents en lien avec la conscience phonologique et la connaissance des lettres.
- **Mathématiques** : nombres jusqu'à **10 et au-delà**, comptine numérique jusqu'à **30**, décomptage de 10 à 1, comptage de 2 en 2 jusqu'à 20, écriture chiffrée de 1 à 10, résolution de problèmes régulière, formes, grandeurs (longueur, masse), motifs répétitifs **et évolutifs**.
- **EVAR** : **au moins 3 séances spécifiques annuelles** (une programmée ici en P1, P3 et P5).
- **Évaluation positive** : observation de ce que dit et fait l'élève, interprétation des progrès par rapport à lui-même ; les fiches proposées complètent — sans remplacer — l'observation en situation (le programme invite à **limiter le recours aux fiches**).

## Sources

- Programme d'enseignement de l'école maternelle (cycle 1), compilation des publications parues au BO n°19 du 7 mai 2026 et au BO n°41 du 31 octobre 2024 (programme EVAR de février 2025).
- Jeu de données officiel en open data : [Programme d'enseignement de l'école maternelle — data.gouv.fr](https://www.data.gouv.fr/datasets/programme-denseignement-de-lecole-maternelle).
