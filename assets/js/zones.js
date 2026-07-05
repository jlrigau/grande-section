/* Adaptation des progressions à la zone de vacances (A, B, C).
 * Dates officielles 2026-2027 issues du jeu de données
 * « fr-en-calendrier-scolaire » (data.education.gouv.fr, ministère de
 * l'Éducation nationale). Rentrée des élèves : arrêté du calendrier scolaire.
 * Premier jour affiché pour une période = jour de reprise ; dernier jour =
 * dernier jour de classe avant les vacances.
 */
(function () {
  'use strict';

  var CAL = {
    rentree: '2026-09-01',           // mardi 1er septembre 2026
    finAnnee: '2027-07-02',          // vendredi 2 juillet 2027 (vacances d'été le 3)
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
    },
    ascension: { debut: '2027-05-06', reprise: '2027-05-10' } // pont : du jeudi 6 au dimanche 9 mai 2027
  };

  var THEMES = ['🏙️ La ville', '🌳 La forêt', '⛰️ La montagne', '🌾 La campagne', '🌊 La mer'];
  var DAY = 86400000;

  function d(iso) { return new Date(iso + 'T00:00:00Z'); }
  function veille(iso) { return new Date(d(iso).getTime() - DAY); }
  function fmt(date, opts) {
    return new Intl.DateTimeFormat('fr-FR', Object.assign({ timeZone: 'UTC' }, opts)).format(date);
  }
  function fmtLong(date) { return fmt(date, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); }
  function fmtCourt(date) { return fmt(date, { weekday: 'short', day: 'numeric', month: 'short' }); }
  function semaines(a, b) { return Math.round(((b.getTime() - a.getTime()) / DAY + 1) / 7); }
  // Le dernier jour de classe est le vendredi précédant le samedi de départ en
  // vacances : « veille » du début officiel des vacances, moins un jour de plus
  // si ce début tombe un samedi déjà vaqué — ici tous les départs sont des
  // samedis, la veille (vendredi) est donc bien le dernier jour de classe.

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
    return 'Zone ' + zone + ' : du ' + fmtCourt(p.debut) + ' au ' + fmtCourt(p.fin) +
      ' ' + fmt(p.fin, { year: 'numeric' }) + ' · ' + p.sem + ' semaines';
  }

  function annoteTitres(zone) {
    var ps = periodes(zone);
    var re = /P[ée]riode\s*([1-5])/i;
    ['h1', 'h2', 'h3'].forEach(function (tag) {
      Array.prototype.forEach.call(document.querySelectorAll('.main-content ' + tag), function (h) {
        var m = h.textContent.match(re);
        if (!m) return;
        var p = ps[parseInt(m[1], 10) - 1];
        var badge = h.querySelector('.zone-badge');
        if (!badge) {
          badge = document.createElement('span');
          badge.className = 'zone-badge';
          h.appendChild(badge);
        }
        badge.textContent = badgeText(p, zone);
      });
    });
  }

  function rendCalendrier(zone) {
    var el = document.getElementById('calendrier-zones');
    if (!el) return;
    var ps = periodes(zone);
    var rows = ps.map(function (p) {
      return '<tr><td><strong>Période ' + p.n + '</strong></td><td>' + THEMES[p.n - 1] + '</td>' +
        '<td>du ' + fmtLong(p.debut) + '<br>au ' + fmtLong(p.fin) + '</td>' +
        '<td style="text-align:center">' + p.sem + '</td></tr>';
    }).join('');
    var vac = [
      ['Toussaint', CAL.toussaint], ['Noël', CAL.noel],
      ['Hiver (zone ' + zone + ')', CAL.hiver[zone]],
      ['Printemps (zone ' + zone + ')', CAL.printemps[zone]]
    ].map(function (v) {
      return '<li><strong>' + v[0] + '</strong> : du ' + fmtCourt(d(v[1].debut)) +
        ' au ' + fmtCourt(veille(v[1].reprise)) + ' (reprise le ' + fmtCourt(d(v[1].reprise)) + ')</li>';
    }).join('');
    el.innerHTML =
      '<table><thead><tr><th>Période</th><th>Thème</th><th>Dates (zone ' + zone + ')</th><th>Semaines</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table>' +
      '<ul class="vac">' + vac +
      '<li><strong>Pont de l\'Ascension</strong> : pas de classe du jeudi 6 au dimanche 9 mai 2027</li>' +
      '<li><strong>Rentrée des élèves</strong> : mardi 1er septembre 2026 · <strong>Fin des cours</strong> : vendredi 2 juillet 2027</li></ul>';
  }

  function applique(zone, memorise) {
    if (memorise) { try { localStorage.setItem('zone-vacances', zone); } catch (e) { /* navigation privée */ } }
    Array.prototype.forEach.call(document.querySelectorAll('.zone-btn'), function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.zone === zone));
    });
    annoteTitres(zone);
    rendCalendrier(zone);
    var hint = document.getElementById('zone-hint');
    if (hint) hint.textContent = 'Toutes les dates de périodes affichées sur ce site correspondent à la zone ' + zone + '. Changez de zone avec les boutons en haut de page.';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var zone = 'A';
    try { zone = localStorage.getItem('zone-vacances') || 'A'; } catch (e) { /* ignore */ }
    if (['A', 'B', 'C'].indexOf(zone) === -1) zone = 'A';
    Array.prototype.forEach.call(document.querySelectorAll('.zone-btn'), function (b) {
      b.addEventListener('click', function () { applique(b.dataset.zone, true); });
    });
    applique(zone, false);
  });
})();
