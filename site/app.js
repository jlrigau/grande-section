/* Ma Grande Section 2026-2027 — application de consultation et d'impression.
 * Dates officielles : calendrier scolaire 2026-2027 (zones A, B, C).
 */
(function () {
  'use strict';

  /* ——— Calendrier officiel 2026-2027 ——— */
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

  /* ——— Les documents de l'année ——— */
  var DOCS = [
    { id: 'accueil', titre: 'Accueil', em: '🏠', groupe: null },
    { id: 'projet-annuel', titre: 'Le projet annuel', em: '📌', md: 'content/01-projet-annuel.md', groupe: 'Pour piloter l’année', desc: 'Le fil rouge, les thèmes, les albums, les chants, les sorties.' },
    { id: 'programmation', titre: 'La programmation annuelle', em: '🗓️', md: 'content/02-programmation-annuelle.md', groupe: 'Pour piloter l’année', desc: 'Tous les domaines période par période, en un coup d’œil.' },
    { id: 'langage', titre: 'Langage oral et écrit', em: '🗣️', md: 'content/03-progressions/01-langage-oral-ecrit.md', groupe: 'Mes progressions', desc: 'Vocabulaire, phonologie, lettres, écriture, compréhension.' },
    { id: 'maths', titre: 'Mathématiques', em: '🔢', md: 'content/03-progressions/02-mathematiques.md', groupe: 'Mes progressions', desc: 'Nombres, problèmes, formes, grandeurs, motifs.' },
    { id: 'eps', titre: 'Activités physiques', em: '🤸', md: 'content/03-progressions/03-activites-physiques.md', groupe: 'Mes progressions', desc: 'Les unités d’apprentissage de l’année, séance par séance.' },
    { id: 'arts', titre: 'Activités artistiques', em: '🎨', md: 'content/03-progressions/04-activites-artistiques.md', groupe: 'Mes progressions', desc: 'Dessin, graphisme, compositions, musique, spectacle vivant.' },
    { id: 'temps-espace', titre: 'Temps et espace', em: '🧭', md: 'content/03-progressions/05-temps-espace.md', groupe: 'Mes progressions', desc: 'Rituels, chronologie, plans, quadrillages, planisphère.' },
    { id: 'monde', titre: 'Le monde du vivant et des objets', em: '🔬', md: 'content/03-progressions/06-monde-vivant-matiere-objets.md', groupe: 'Mes progressions', desc: 'Élevages, plantations, matière, fabrications.' },
    { id: 'evar', titre: 'Vie affective et relationnelle', em: '💛', md: 'content/03-progressions/07-evar.md', groupe: 'Mes progressions', desc: 'Les 3 séances obligatoires et le fil continu.' },
    { id: 'eval-guide', titre: 'Mode d’emploi et livret de suivi', em: '📋', md: 'content/04-evaluations/00-mode-emploi-et-livret-de-suivi.md', groupe: 'Mes évaluations', desc: 'Principes, codage, livret annuel, grille de vocabulaire.' },
    { id: 'eval-p1', titre: 'Période 1 · La ville', em: '🏙️', md: 'content/04-evaluations/periode-1-ville.md', groupe: 'Mes évaluations', desc: '13 fiches + grilles d’observation (octobre).' },
    { id: 'eval-p2', titre: 'Période 2 · La forêt', em: '🌳', md: 'content/04-evaluations/periode-2-foret.md', groupe: 'Mes évaluations', desc: '14 fiches + grilles d’observation (décembre).' },
    { id: 'eval-p3', titre: 'Période 3 · La montagne', em: '⛰️', md: 'content/04-evaluations/periode-3-montagne.md', groupe: 'Mes évaluations', desc: '15 fiches + grilles d’observation (février).' },
    { id: 'eval-p4', titre: 'Période 4 · La campagne', em: '🌾', md: 'content/04-evaluations/periode-4-campagne.md', groupe: 'Mes évaluations', desc: '15 fiches + grilles d’observation (avril).' },
    { id: 'eval-p5', titre: 'Période 5 · La mer', em: '🌊', md: 'content/04-evaluations/periode-5-mer.md', groupe: 'Mes évaluations', desc: 'Bilan de fin de GS + liaison CP (juin).' }
  ];

  var etat = { zone: 'A', doc: 'accueil' };
  var cacheMd = {};

  /* ——— Dates ——— */
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

  /* ——— Navigation ——— */
  function construireMenu() {
    var nav = document.getElementById('sidebar');
    var html = '';
    var groupeCourant = null;
    DOCS.forEach(function (doc) {
      if (doc.groupe !== groupeCourant) {
        groupeCourant = doc.groupe;
        if (groupeCourant) html += '<div class="groupe">' + groupeCourant + '</div>';
      }
      html += '<a href="#/' + doc.id + '" data-doc="' + doc.id + '"><span class="em">' + doc.em + '</span><span>' + doc.titre + '</span></a>';
    });
    nav.innerHTML = html;
  }

  function majMenuActif() {
    document.querySelectorAll('.sidebar a').forEach(function (a) {
      a.classList.toggle('actif', a.dataset.doc === etat.doc);
    });
  }

  /* ——— Rendu ——— */
  function annoteTitres(racine) {
    var ps = periodes(etat.zone);
    var re = /P[ée]riode\s*([1-5])/i;
    racine.querySelectorAll('h1, h2, h3').forEach(function (h) {
      var m = h.textContent.match(re);
      if (!m) return;
      var p = ps[parseInt(m[1], 10) - 1];
      var badge = h.querySelector('.zone-badge');
      if (!badge) { badge = document.createElement('span'); badge.className = 'zone-badge'; h.appendChild(badge); }
      badge.textContent = badgeText(p, etat.zone);
    });
  }

  function nettoieMarkdown(md) {
    // Retire les éléments propres au dépôt (liens internes .md, blocs HTML de l'ancien site)
    return md
      .replace(/\[([^\]]+)\]\((?:\.\/)?[^)]+\.md\)/g, '$1')
      .replace(/<div id="calendrier-zones">[\s\S]*?<\/div>/g, '')
      .replace(/<p id="zone-hint"[^>]*><\/p>/g, '');
  }

  function chargeMd(doc) {
    if (cacheMd[doc.md]) return Promise.resolve(cacheMd[doc.md]);
    return fetch(doc.md).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.text();
    }).then(function (t) { cacheMd[doc.md] = t; return t; });
  }

  function rendDocument(doc) {
    var contenu = document.getElementById('contenu');
    contenu.innerHTML = '<p class="chargement">Chargement…</p>';
    chargeMd(doc).then(function (md) {
      contenu.innerHTML = marked.parse(nettoieMarkdown(md));
      annoteTitres(contenu);
      window.scrollTo(0, 0);
    }).catch(function () {
      contenu.innerHTML = '<p>Impossible de charger ce document. Vérifiez votre connexion puis rechargez la page.</p>';
    });
  }

  function periodeDuJour(ps) {
    var auj = new Date();
    var t = Date.UTC(auj.getFullYear(), auj.getMonth(), auj.getDate());
    for (var i = 0; i < ps.length; i++) {
      if (t >= ps[i].debut.getTime() && t <= ps[i].fin.getTime()) return ps[i];
    }
    return null;
  }

  function rendAccueil() {
    var ps = periodes(etat.zone);
    var lignes = ps.map(function (p) {
      return '<tr><td><strong>Période ' + p.n + '</strong></td><td>' + THEMES[p.n - 1] + '</td>' +
        '<td>du ' + fmtLong(p.debut) + '<br>au ' + fmtLong(p.fin) + '</td>' +
        '<td style="text-align:center">' + p.sem + '</td></tr>';
    }).join('');
    var vac = [
      ['Vacances de la Toussaint', CAL.toussaint], ['Vacances de Noël', CAL.noel],
      ['Vacances d’hiver (zone ' + etat.zone + ')', CAL.hiver[etat.zone]],
      ['Vacances de printemps (zone ' + etat.zone + ')', CAL.printemps[etat.zone]]
    ].map(function (v) {
      return '<li><strong>' + v[0] + '</strong> : du ' + fmtCourt(d(v[1].debut)) + ' au ' + fmtCourt(veille(v[1].reprise)) +
        ' — reprise le ' + fmtCourt(d(v[1].reprise)) + '</li>';
    }).join('');
    var pj = periodeDuJour(ps);
    var bandeau = pj
      ? '<div class="periode-actuelle">📍 Nous sommes en période ' + pj.n + ' — ' + THEMES[pj.n - 1] + ' (jusqu’au ' + fmtLong(pj.fin) + ').</div>'
      : '';
    var cartes = DOCS.filter(function (doc) { return doc.md; }).map(function (doc) {
      return '<a class="carte" href="#/' + doc.id + '"><span class="em">' + doc.em + '</span>' +
        '<span class="t">' + doc.titre + '</span><div class="d">' + doc.desc + '</div></a>';
    }).join('');

    document.getElementById('contenu').innerHTML =
      '<div class="accueil-hero">' +
      '<h1>🐾 À la découverte de la faune et de la flore</h1>' +
      '<p>Bienvenue ! Vous trouverez ici tout le matériel de votre année de Grande Section : le projet annuel, ' +
      'la programmation, les progressions de chaque domaine et les fiches d’évaluation de chaque période.</p>' +
      '<p class="zone-hint">🅰️🅱️©️ Choisissez votre <strong>zone de vacances</strong> en haut de page : toutes les dates ' +
      'de périodes s’adaptent automatiquement, sur toutes les pages. Chaque document peut être <strong>enregistré en PDF</strong> ' +
      'avec le bouton bleu 📄.</p>' + bandeau +
      '</div>' +
      '<h2>Mon calendrier de l’année <span class="zone-badge">Zone ' + etat.zone + '</span></h2>' +
      '<table><thead><tr><th>Période</th><th>Thème</th><th>Dates</th><th>Semaines</th></tr></thead><tbody>' + lignes + '</tbody></table>' +
      '<ul class="vac-liste">' + vac +
      '<li><strong>Pont de l’Ascension</strong> : pas de classe du jeudi 6 au dimanche 9 mai 2027</li>' +
      '<li><strong>Rentrée des élèves</strong> : mardi 1er septembre 2026 — <strong>fin des cours</strong> : vendredi 2 juillet 2027</li></ul>' +
      '<h2>Mes documents</h2><div class="cartes">' + cartes + '</div>';
    window.scrollTo(0, 0);
  }

  function rend() {
    var doc = DOCS.find(function (x) { return x.id === etat.doc; }) || DOCS[0];
    etat.doc = doc.id;
    majMenuActif();
    document.getElementById('fil').textContent = doc.groupe ? doc.groupe + ' › ' + doc.titre : 'Année 2026-2027';
    document.getElementById('print-header').innerHTML =
      '<span>Grande Section 2026-2027 · À la découverte de la faune et de la flore</span>' +
      '<span>Zone ' + etat.zone + '</span>';
    if (doc.md) rendDocument(doc); else rendAccueil();
    document.getElementById('sidebar').classList.remove('ouvert');
  }

  /* ——— Zone ——— */
  function appliqueZone(zone, memorise) {
    etat.zone = zone;
    if (memorise) { try { localStorage.setItem('zone-vacances', zone); } catch (e) { /* ignore */ } }
    document.querySelectorAll('.zone-btn').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.zone === zone));
    });
    rend();
  }

  /* ——— Démarrage ——— */
  document.addEventListener('DOMContentLoaded', function () {
    marked.use({ gfm: true, breaks: false });
    construireMenu();

    var zone = 'A';
    try { zone = localStorage.getItem('zone-vacances') || 'A'; } catch (e) { /* ignore */ }
    if (['A', 'B', 'C'].indexOf(zone) === -1) zone = 'A';

    document.querySelectorAll('.zone-btn').forEach(function (b) {
      b.addEventListener('click', function () { appliqueZone(b.dataset.zone, true); });
    });
    document.getElementById('btn-pdf').addEventListener('click', function () { window.print(); });
    document.getElementById('menu-toggle').addEventListener('click', function () {
      document.getElementById('sidebar').classList.toggle('ouvert');
    });
    window.addEventListener('hashchange', function () {
      etat.doc = (location.hash || '#/accueil').replace('#/', '') || 'accueil';
      rend();
    });

    etat.doc = (location.hash || '#/accueil').replace('#/', '') || 'accueil';
    appliqueZone(zone, false);
  });
})();
