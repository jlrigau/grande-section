/* Données et fonctions partagées entre l'application (app.js) et la vue
 * d'impression (imprimer.js). Dates officielles : calendrier scolaire
 * 2026-2027 (zones A, B, C).
 */
var GS = (function () {
  'use strict';

  var CAL = {
    rentree: '2026-09-01',
    finAnnee: '2027-07-02',
    toussaint: { debut: '2026-10-17', reprise: '2026-11-02' },
    noel: { debut: '2026-12-19', reprise: '2027-01-04' },
    hiver: {
      A: { debut: '2027-02-13', reprise: '2027-03-01' },
      B: { debut: '2027-02-20', reprise: '2027-03-08' },
      C: { debut: '2027-02-06', reprise: '2027-02-22' }
    },
    printemps: {
      A: { debut: '2027-04-10', reprise: '2027-04-26' },
      B: { debut: '2027-04-17', reprise: '2027-05-03' },
      C: { debut: '2027-04-03', reprise: '2027-04-19' }
    }
  };
  var THEMES = ['🏙️ La ville', '🌳 La forêt', '⛰️ La montagne', '🌾 La campagne', '🌊 La mer'];
  var DAY = 86400000;

  var DOCS = [
    { id: 'accueil', titre: 'Accueil', em: '🏠', groupe: null },
    { id: 'projet-annuel', titre: 'Le projet annuel', em: '📌', md: 'content/01-projet-annuel.md', groupe: 'Pour piloter l’année', desc: 'Le fil rouge, les thèmes, les albums, les chants, les sorties.' },
    { id: 'programmation', titre: 'La programmation annuelle', em: '🗓️', md: 'content/02-programmation-annuelle.md', groupe: 'Pour piloter l’année', desc: 'Tous les domaines période par période, en un coup d’œil.' },
    { id: 'langage', parPeriode: true, titre: 'Langage oral et écrit', em: '🗣️', md: 'content/03-progressions/01-langage-oral-ecrit.md', groupe: 'Mes progressions', desc: 'Vocabulaire, phonologie, lettres, écriture, compréhension.' },
    { id: 'maths', parPeriode: true, titre: 'Mathématiques', em: '🔢', md: 'content/03-progressions/02-mathematiques.md', groupe: 'Mes progressions', desc: 'Nombres, problèmes, formes, grandeurs, motifs.' },
    { id: 'eps', parPeriode: true, titre: 'Activités physiques', em: '🤸', md: 'content/03-progressions/03-activites-physiques.md', groupe: 'Mes progressions', desc: 'Les unités d’apprentissage de l’année, séance par séance.' },
    { id: 'arts', parPeriode: true, titre: 'Activités artistiques', em: '🎨', md: 'content/03-progressions/04-activites-artistiques.md', groupe: 'Mes progressions', desc: 'Dessin, graphisme, compositions, musique, spectacle vivant.' },
    { id: 'temps-espace', parPeriode: true, titre: 'Temps et espace', em: '🧭', md: 'content/03-progressions/05-temps-espace.md', groupe: 'Mes progressions', desc: 'Rituels, chronologie, plans, quadrillages, planisphère.' },
    { id: 'monde', parPeriode: true, titre: 'Le monde du vivant et des objets', em: '🔬', md: 'content/03-progressions/06-monde-vivant-matiere-objets.md', groupe: 'Mes progressions', desc: 'Élevages, plantations, matière, fabrications.' },
    { id: 'evar', titre: 'Vie affective et relationnelle', em: '💛', md: 'content/03-progressions/07-evar.md', groupe: 'Mes progressions', desc: 'Les 3 séances obligatoires et le fil continu.' },
    { id: 'eval-guide', titre: 'Mode d’emploi et livret de suivi', em: '📋', md: 'content/04-evaluations/00-mode-emploi-et-livret-de-suivi.md', groupe: 'Mes évaluations', desc: 'Principes, codage, livret annuel, grille de vocabulaire.' },
    { id: 'eval-p1', titre: 'Période 1 · La ville', em: '🏙️', md: 'content/04-evaluations/periode-1-ville.md', groupe: 'Mes évaluations', desc: '13 fiches + grilles d’observation (octobre).', fiches: 1 },
    { id: 'eval-p2', titre: 'Période 2 · La forêt', em: '🌳', md: 'content/04-evaluations/periode-2-foret.md', groupe: 'Mes évaluations', desc: '14 fiches + grilles d’observation (décembre).', fiches: 2 },
    { id: 'eval-p3', titre: 'Période 3 · La montagne', em: '⛰️', md: 'content/04-evaluations/periode-3-montagne.md', groupe: 'Mes évaluations', desc: '15 fiches + grilles d’observation (février).', fiches: 3 },
    { id: 'eval-p4', titre: 'Période 4 · La campagne', em: '🌾', md: 'content/04-evaluations/periode-4-campagne.md', groupe: 'Mes évaluations', desc: '15 fiches + grilles d’observation (avril).', fiches: 4 },
    { id: 'eval-p5', titre: 'Période 5 · La mer', em: '🌊', md: 'content/04-evaluations/periode-5-mer.md', groupe: 'Mes évaluations', desc: 'Bilan de fin de GS + liaison CP (juin).', fiches: 5 }
  ];

  function d(iso) { return new Date(iso + 'T00:00:00Z'); }
  function veille(iso) { return new Date(d(iso).getTime() - DAY); }
  function fmt(date, opts) { return new Intl.DateTimeFormat('fr-FR', Object.assign({ timeZone: 'UTC' }, opts)).format(date); }
  function fmtLong(date) { return fmt(date, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); }
  function fmtCourt(date) { return fmt(date, { weekday: 'short', day: 'numeric', month: 'short' }); }
  function semaines(a, b) { return Math.round(((b.getTime() - a.getTime()) / DAY + 1) / 7); }

  function periodes(zone) {
    return [
      { n: 1, debut: d(CAL.rentree), fin: veille(CAL.toussaint.debut) },
      { n: 2, debut: d(CAL.toussaint.reprise), fin: veille(CAL.noel.debut) },
      { n: 3, debut: d(CAL.noel.reprise), fin: veille(CAL.hiver[zone].debut) },
      { n: 4, debut: d(CAL.hiver[zone].reprise), fin: veille(CAL.printemps[zone].debut) },
      { n: 5, debut: d(CAL.printemps[zone].reprise), fin: d(CAL.finAnnee) }
    ].map(function (p) { p.sem = semaines(p.debut, p.fin); return p; });
  }

  function badgeText(p, zone) {
    return 'Zone ' + zone + ' : du ' + fmtCourt(p.debut) + ' au ' + fmtCourt(p.fin) + ' ' + fmt(p.fin, { year: 'numeric' }) + ' · ' + p.sem + ' semaines';
  }

  function annoteTitres(racine, zone) {
    var ps = periodes(zone);
    var re = /P[ée]riode\s*([1-5])/i;
    racine.querySelectorAll('h1, h2, h3').forEach(function (h) {
      var m = h.textContent.match(re);
      if (!m) return;
      var p = ps[parseInt(m[1], 10) - 1];
      var badge = h.querySelector('.zone-badge');
      if (!badge) { badge = document.createElement('span'); badge.className = 'zone-badge'; h.appendChild(badge); }
      badge.textContent = badgeText(p, zone);
    });
  }

  function nettoieMarkdown(md) {
    return md
      .replace(/\[([^\]]+)\]\((?:\.\/)?[^)]+\.md\)/g, '$1')
      .replace(/<div id="calendrier-zones">[\s\S]*?<\/div>/g, '')
      .replace(/<p id="zone-hint"[^>]*><\/p>/g, '');
  }

  return {
    CAL: CAL, THEMES: THEMES, DOCS: DOCS,
    d: d, veille: veille, fmt: fmt, fmtLong: fmtLong, fmtCourt: fmtCourt,
    periodes: periodes, badgeText: badgeText, annoteTitres: annoteTitres,
    nettoieMarkdown: nettoieMarkdown
  };
})();
