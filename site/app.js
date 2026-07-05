/* Ma Grande Section 2026-2027 — application de consultation.
 * Les données partagées (calendrier, documents) sont dans commun.js (GS).
 */
(function () {
  'use strict';

  var etat = { zone: 'A', doc: 'accueil' };
  var cacheMd = {};

  /* ——— Navigation ——— */
  function construireMenu() {
    var nav = document.getElementById('sidebar');
    var html = '';
    var groupeCourant = null;
    GS.DOCS.forEach(function (doc) {
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

  /* ——— Rendu des documents ——— */
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
      contenu.innerHTML = marked.parse(GS.nettoieMarkdown(md));
      GS.annoteTitres(contenu, etat.zone);
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
    var ps = GS.periodes(etat.zone);
    var lignes = ps.map(function (p) {
      return '<tr><td><strong>Période ' + p.n + '</strong></td><td>' + GS.THEMES[p.n - 1] + '</td>' +
        '<td>du ' + GS.fmtLong(p.debut) + '<br>au ' + GS.fmtLong(p.fin) + '</td>' +
        '<td style="text-align:center">' + p.sem + '</td></tr>';
    }).join('');
    var vac = [
      ['Vacances de la Toussaint', GS.CAL.toussaint], ['Vacances de Noël', GS.CAL.noel],
      ['Vacances d’hiver (zone ' + etat.zone + ')', GS.CAL.hiver[etat.zone]],
      ['Vacances de printemps (zone ' + etat.zone + ')', GS.CAL.printemps[etat.zone]]
    ].map(function (v) {
      return '<li><strong>' + v[0] + '</strong> : du ' + GS.fmtCourt(GS.d(v[1].debut)) + ' au ' + GS.fmtCourt(GS.veille(v[1].reprise)) +
        ' — reprise le ' + GS.fmtCourt(GS.d(v[1].reprise)) + '</li>';
    }).join('');
    var pj = periodeDuJour(ps);
    var bandeau = pj
      ? '<div class="periode-actuelle">📍 Nous sommes en période ' + pj.n + ' — ' + GS.THEMES[pj.n - 1] + ' (jusqu’au ' + GS.fmtLong(pj.fin) + ').</div>'
      : '';
    var cartes = GS.DOCS.filter(function (doc) { return doc.md; }).map(function (doc) {
      return '<a class="carte" href="#/' + doc.id + '"><span class="em">' + doc.em + '</span>' +
        '<span class="t">' + doc.titre + '</span><div class="d">' + doc.desc + '</div></a>';
    }).join('');
    var fiches = [1, 2, 3, 4, 5].map(function (n) {
      return '<a class="carte" href="pdf/fiches-entrainement-periode-' + n + '.pdf" download><span class="em">✏️</span>' +
        '<span class="t">Entraînement · Période ' + n + '</span><div class="d">' + GS.THEMES[n - 1] +
        ' — 12 fiches avec sous-objectifs, 2 niveaux (★ je m’entraîne / ★★ je consolide) et défis.</div></a>' +
        '<a class="carte" href="pdf/fiches-eleve-periode-' + n + '.pdf" download><span class="em">🖨️</span>' +
        '<span class="t">Évaluation · Période ' + n + '</span><div class="d">' + GS.THEMES[n - 1] +
        ' — les fiches élève de l’évaluation de fin de période.</div></a>';
    }).join('');

    document.getElementById('contenu').innerHTML =
      '<div class="accueil-hero">' +
      '<h1>🐾 À la découverte de la faune et de la flore</h1>' +
      '<p>Bienvenue ! Vous trouverez ici tout le matériel de votre année de Grande Section : le projet annuel, ' +
      'la programmation, les progressions de chaque domaine, les fiches d’évaluation et les fiches élève de chaque période.</p>' +
      '<p class="zone-hint">🅰️🅱️©️ Choisissez votre <strong>zone de vacances</strong> en haut de page : toutes les dates ' +
      's’adaptent automatiquement. Chaque document se télécharge en <strong>PDF prêt à imprimer</strong> avec le bouton bleu 📥.</p>' + bandeau +
      '</div>' +
      '<h2>Mon calendrier de l’année <span class="zone-badge">Zone ' + etat.zone + '</span></h2>' +
      '<table><thead><tr><th>Période</th><th>Thème</th><th>Dates</th><th>Semaines</th></tr></thead><tbody>' + lignes + '</tbody></table>' +
      '<ul class="vac-liste">' + vac +
      '<li><strong>Pont de l’Ascension</strong> : pas de classe du jeudi 6 au dimanche 9 mai 2027</li>' +
      '<li><strong>Rentrée des élèves</strong> : mardi 1er septembre 2026 — <strong>fin des cours</strong> : vendredi 2 juillet 2027</li></ul>' +
      '<h2>🖨️ Mes fiches élève à imprimer</h2>' +
      '<p>Des feuilles individuelles à photocopier (l’enseignante donne la consigne à l’oral, elle est rappelée sur la fiche pour les familles). ' +
      'Pour chaque période : un cahier d’<strong>entraînement</strong> (12 fiches en 2 séries, avec sous-objectifs et défis ⭐ — de quoi travailler 2 à 3 fiches par semaine) ' +
      'et un cahier d’<strong>évaluation</strong> de fin de période.</p>' +
      '<div class="cartes">' + fiches + '</div>' +
      '<h2>Mes documents</h2><div class="cartes">' + cartes + '</div>';
    window.scrollTo(0, 0);
  }

  function rend() {
    var doc = GS.DOCS.find(function (x) { return x.id === etat.doc; }) || GS.DOCS[0];
    etat.doc = doc.id;
    majMenuActif();
    document.getElementById('fil').textContent = doc.groupe ? doc.groupe + ' › ' + doc.titre : 'Année 2026-2027';

    var btnPdf = document.getElementById('btn-pdf');
    var btnFiches = document.getElementById('btn-fiches');
    if (doc.md) {
      btnPdf.hidden = false;
      btnPdf.href = 'pdf/zone-' + etat.zone + '/' + doc.id + '.pdf';
      btnPdf.setAttribute('download', 'GS-2026-2027-' + doc.id + '-zone-' + etat.zone + '.pdf');
    } else {
      btnPdf.hidden = true;
    }
    var btnEntr = document.getElementById('btn-entrainement');
    if (doc.fiches) {
      btnFiches.hidden = false;
      btnFiches.href = 'pdf/fiches-eleve-periode-' + doc.fiches + '.pdf';
      btnFiches.setAttribute('download', 'GS-fiches-eleve-periode-' + doc.fiches + '.pdf');
      btnEntr.hidden = false;
      btnEntr.href = 'pdf/fiches-entrainement-periode-' + doc.fiches + '.pdf';
      btnEntr.setAttribute('download', 'GS-fiches-entrainement-periode-' + doc.fiches + '.pdf');
    } else {
      btnFiches.hidden = true;
      btnEntr.hidden = true;
    }

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
