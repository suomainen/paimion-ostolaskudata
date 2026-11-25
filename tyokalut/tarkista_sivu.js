// Selaintarkistus valmiille index.html:lle: saavutettavuus (axe), näppäimistökäyttö,
// linkkien pysyvyys, kielet ja ulkoasu sekä analyysien luvut.
//
// Asennus kerran repon juuressa:   npm install --no-save playwright axe-core && npx playwright install chromium
// Ajo:                             node tyokalut/tarkista_sivu.js
//
// Palauttaa virhekoodin 1, jos jokin tarkistus ei mene läpi.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SIVU = 'file://' + path.resolve(__dirname, '..', 'index.html').replace(/\\/g, '/');
const AXE = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const LEVEYDET = [1280, 375];
let virheet = 0;
const tarkista = (ehto, kuvaus, lisa = '') => { console.log((ehto ? '  ok   ' : '  VIRHE ') + kuvaus + (ehto ? '' : ' ' + lisa)); if (!ehto) virheet++; };

async function axe(sivu, nimi) {
  await sivu.addScriptTag({ content: AXE });
  const r = await sivu.evaluate(async () => await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } }));
  tarkista(r.violations.length === 0, `axe: ${nimi}`, r.violations.map(v => `${v.id} ×${v.nodes.length} (${v.nodes[0].target.join(' ')})`).join('; '));
}
const avaa = async (sivu, hash = '') => { await sivu.goto('about:blank'); await sivu.goto(SIVU + hash); await sivu.waitForTimeout(700); };
const kohdistus = sivu => sivu.evaluate(() => { const a = document.activeElement; return a.tagName + (a.id ? '#' + a.id : '') + (a.className ? '.' + String(a.className).split(' ')[0] : ''); });

(async () => {
  const selain = await chromium.launch();

  for (const leveys of LEVEYDET) {
    console.log(`\nSaavutettavuus ${leveys} px`);
    const sivu = await selain.newPage({ viewport: { width: leveys, height: 900 } });
    const jsVirheet = []; sivu.on('pageerror', e => jsVirheet.push(e.message));
    const pyynnot = []; await sivu.route('**/*', r => { const u = r.request().url(); if (!u.startsWith('file:') && !u.startsWith('data:')) { pyynnot.push(u); return r.abort(); } return r.continue(); });
    await avaa(sivu); await axe(sivu, 'yhteenveto');
    await avaa(sivu, '#vuosi=2024&tili=4340&kk=6'); await axe(sivu, 'rajattu yhteenveto');
    await avaa(sivu, '#nakyma=analyysit'); await axe(sivu, 'analyysit');
    await avaa(sivu, '#nakyma=analyysit&jako=tilil&vuosi=2020'); await axe(sivu, 'analyysit, ensimmäinen vuosi');
    await avaa(sivu); await sivu.click('#supTable .rowbtn'); await sivu.waitForTimeout(300); await axe(sivu, 'toimittajan ikkuna');
    tarkista(jsVirheet.length === 0, 'ei JavaScript-virheitä', jsVirheet.join('; '));
    tarkista(pyynnot.length === 0, 'sivu ei hae mitään verkosta', pyynnot.join(', '));
    await sivu.close();
  }

  console.log('\nKapea näyttö');
  for (const hash of ['', '#nakyma=analyysit']) {
    const kapea = await selain.newPage({ viewport: { width: 320, height: 700 } });
    await avaa(kapea, hash);
    tarkista(await kapea.evaluate(() => document.documentElement.scrollWidth) <= 320, `ei vaakavieritystä 320 px leveydellä ${hash || '(yhteenveto)'}`);
    await kapea.close();
  }

  console.log('\nNäppäimistö');
  const s = await selain.newPage({ viewport: { width: 1280, height: 900 } });
  await avaa(s);
  await s.keyboard.press('Tab'); tarkista((await kohdistus(s)).startsWith('A.skip'), 'ensimmäinen sarkain vie ohituslinkkiin');
  await s.keyboard.press('Enter'); tarkista((await kohdistus(s)).startsWith('MAIN#sisalto'), 'ohituslinkki siirtää kohdistuksen sisältöön');
  await s.focus('#supTable .rowbtn'); await s.keyboard.press('Enter'); await s.waitForTimeout(300);
  tarkista(await kohdistus(s) === 'BUTTON#dClose', 'toimittajan ikkuna avautuu ja kohdistus siirtyy siihen');
  tarkista(await s.evaluate(() => document.getElementById('sisalto').inert), 'tausta ei ole käytettävissä ikkunan ollessa auki');
  tarkista(/toimittaja=\d{7}-\d/.test(await s.evaluate(() => location.hash)), 'avattu toimittaja näkyy osoitteessa');
  await s.keyboard.press('Escape'); await s.waitForTimeout(200);
  tarkista((await kohdistus(s)).startsWith('BUTTON.rowbtn'), 'Esc sulkee ikkunan ja palauttaa kohdistuksen riville');
  await s.focus('#tiliTable .rowbtn'); await s.keyboard.press('Enter'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => document.activeElement.getAttribute('aria-pressed')) === 'true', 'tilin valinta näppäimistöllä säilyttää kohdistuksen ja kertoo tilan');
  tarkista((await s.$eval('#live', e => e.textContent)).startsWith('Näkymä päivitetty'), 'ruudunlukijalle tilaviesti rajauksen jälkeen');
  await s.focus('#t-yhteenveto'); await s.keyboard.press('ArrowRight'); await s.waitForTimeout(300);
  tarkista(await kohdistus(s) === 'BUTTON#t-analyysit' && !(await s.evaluate(() => document.getElementById('p-analyysit').hidden)), 'välilehti vaihtuu nuolinäppäimellä');

  console.log('\nPysyvät linkit');
  await avaa(s, '#vuosi=2023&kunta=Paimio&tili=4340&nakyma=analyysit&jako=tilil&mittari_kunta=n&alue=fi');
  const tila = await s.evaluate(() => ({ vuosi: Y[S.year], kunta: D.kunta[S.kunta], tili: D.tilil[S.tilil], view: S.view, adim: S.adim, mittari: mode.kunta, alue: mode.zoom, hash: decodeURIComponent(location.hash) }));
  tarkista(tila.vuosi === 2023 && tila.kunta === 'Paimio' && tila.tili.startsWith('4340 ') && tila.view === 'analyysit' && tila.adim === 'tilil' && tila.mittari === 'n' && tila.alue === 'fi', 'osoitteen tila luetaan oikein', JSON.stringify(tila));
  tarkista(['vuosi=2023', 'kunta=Paimio', 'tili=4340', 'nakyma=analyysit', 'jako=tilil', 'mittari_kunta=n', 'alue=fi'].every(o => tila.hash.includes(o)), 'sama tila kirjoitetaan takaisin osoitteeseen', tila.hash);
  await avaa(s, '#vuosi=1999&kunta=Olematon&tili=0000'); tarkista(await s.evaluate(() => Y[S.year] === Y[Y.length - 1] && S.kunta === null && S.tilil === null), 'tuntemattomat arvot ohitetaan');
  await avaa(s, '#year=2'); tarkista(await s.evaluate(() => S.year === 2), 'vanha linkkimuoto (year=järjestysnumero) toimii');
  const yt = await s.evaluate(() => SUP.find(x => x[P.YT])[P.YT]);
  await avaa(s, '#toimittaja=' + yt); tarkista(await s.evaluate(() => document.getElementById('drawer').classList.contains('open')), 'linkki avaa toimittajan ikkunan');

  console.log('\nKielet ja ulkoasu');
  for (const leveys of LEVEYDET) {
    const k = await selain.newPage({ viewport: { width: leveys, height: 900 } });
    const virh = []; k.on('pageerror', e => virh.push(e.message));
    for (const kieli of ['sv', 'en']) {
      await avaa(k, '#kieli=' + kieli); await axe(k, `${kieli}, yhteenveto ${leveys} px`);
      await avaa(k, `#kieli=${kieli}&nakyma=analyysit&vuosi=2024&tili=4340`); await axe(k, `${kieli}, analyysit ${leveys} px`);
    }
    await avaa(k); await k.click('#teema'); await k.waitForTimeout(300); await axe(k, `tumma ulkoasu, yhteenveto ${leveys} px`);
    await avaa(k, '#nakyma=analyysit&kunta=Paimio'); await axe(k, `tumma ulkoasu, analyysit ${leveys} px`);
    await avaa(k); await k.click('#supTable .rowbtn'); await k.waitForTimeout(300); await axe(k, `tumma ulkoasu, toimittajan ikkuna ${leveys} px`);
    if (leveys < 1000) { await avaa(k); await k.click('#menuBtn'); await k.waitForTimeout(200); await axe(k, `valikko auki ${leveys} px`); }
    tarkista(virh.length === 0, `ei JavaScript-virheitä (${leveys} px)`, virh.join('; '));
    await k.close();
  }
  const k = await selain.newPage({ viewport: { width: 1280, height: 900 } });
  await avaa(k);
  const puuttuvat = await k.evaluate(() => {
    const avaimet = new Set([...Object.keys(T.fi)]);
    document.querySelectorAll('[data-t]').forEach(e => avaimet.add(e.dataset.t));
    document.querySelectorAll('[data-ta]').forEach(e => e.dataset.ta.split(';').forEach(p => avaimet.add(p.split(':')[1])));
    const out = [];
    for (const kieli of ['sv', 'en']) for (const a of avaimet) {
      const v = T[kieli][a], f = T.fi[a];
      if (v === undefined || typeof v !== typeof f) out.push(kieli + ':' + a);
      else if (f && typeof f === 'object') for (const x of Object.keys(f)) if (v[x] === undefined) out.push(`${kieli}:${a}.${x}`);
    }
    return out;
  });
  tarkista(puuttuvat.length === 0, 'jokaisella tekstillä on ruotsin ja englannin käännös', puuttuvat.join(', '));
  tarkista(await k.evaluate(() => document.documentElement.lang === 'fi' && document.getElementById('kieliNote').hidden), 'oletuskieli on suomi');
  await k.click('#kielet [data-kieli="sv"]'); await k.waitForTimeout(300);
  const sv = await k.evaluate(() => ({ lang: document.documentElement.lang, h1: document.querySelector('h1').textContent, hash: location.hash, painettu: document.querySelector('#kielet [data-kieli="sv"]').getAttribute('aria-pressed'),
    kpi: document.querySelector('.kpi .l').textContent, th: document.querySelector('#supTable th').textContent, fi: !!document.querySelector('#tiliTable td.name[lang="fi"]'), live: document.getElementById('live').textContent, title: document.title }));
  tarkista(sv.lang === 'sv' && sv.h1.includes('inköpsfakturor') && sv.kpi === 'Inköp totalt' && sv.th === 'Leverantör' && sv.painettu === 'true' && sv.title.includes('inköpsfakturor'), 'kielen vaihto ruotsiksi kääntää otsikot, tunnusluvut ja taulukot', JSON.stringify(sv));
  tarkista(sv.hash.includes('kieli=sv'), 'kieli tallentuu osoitteeseen', sv.hash);
  tarkista(sv.fi, 'suomenkieliset aineiston arvot on merkitty lang="fi"');
  tarkista(sv.live.startsWith('Sidans språk är svenska'), 'kielen vaihdosta tilaviesti ruudunlukijalle', sv.live);
  await avaa(k); tarkista(await k.evaluate(() => document.documentElement.lang) === 'sv', 'kielivalinta muistetaan selaimessa');
  await avaa(k, '#kieli=en&kunta=Turku'); 
  const en = await k.evaluate(() => ({ lang: document.documentElement.lang, kunta: D.kunta[S.kunta], hash: decodeURIComponent(location.hash), eur: document.querySelector('.kpi .v').textContent }));
  tarkista(en.lang === 'en' && en.kunta === 'Turku' && en.hash.includes('kunta=Turku') && /^\d+\.\d M€$/.test(en.eur), 'osoitteen kieli ohittaa muistetun, rajaukset pysyvät suomenkielisillä nimillä ja luvut muotoillaan kielen mukaan', JSON.stringify(en));
  await k.click('#kielet [data-kieli="fi"]'); await k.waitForTimeout(300);
  tarkista(await k.evaluate(() => document.documentElement.lang === 'fi' && document.querySelector('h1').textContent === 'Paimion kaupungin ostolaskut' && !location.hash.includes('kieli=')), 'paluu suomeen palauttaa alkuperäiset tekstit');
  await k.click('#teema'); await k.waitForTimeout(200);
  tarkista(await k.evaluate(() => document.documentElement.dataset.teema === 'tumma' && document.getElementById('teema').getAttribute('aria-pressed') === 'true'), 'tumma ulkoasu kytkeytyy painikkeesta');
  await avaa(k); tarkista(await k.evaluate(() => document.documentElement.dataset.teema === 'tumma' && getComputedStyle(document.body).backgroundColor !== 'rgb(255, 255, 255)'), 'ulkoasun valinta muistetaan selaimessa');
  await k.click('#teema'); await k.waitForTimeout(200);
  tarkista(await k.evaluate(() => !document.documentElement.dataset.teema && getComputedStyle(document.body).backgroundColor === 'rgb(255, 255, 255)'), 'paluu vaaleaan ulkoasuun');
  await avaa(k, '#vuosi=2023&tili=4340'); await k.click('#valikko a[data-nakyma="analyysit"]'); await k.waitForTimeout(300);
  const nav = await k.evaluate(() => ({ hash: location.hash, view: S.view, f: document.activeElement.id }));
  tarkista(nav.view === 'analyysit' && nav.hash.includes('vuosi=2023') && nav.hash.includes('tili=4340') && nav.f === 't-analyysit', 'yläpalkin linkki vaihtaa välilehden ja säilyttää rajaukset osoitteessa', JSON.stringify(nav));
  await k.close();
  const m = await selain.newPage({ viewport: { width: 375, height: 700 } });
  await avaa(m); await m.focus('#menuBtn'); await m.keyboard.press('Enter'); await m.waitForTimeout(200);
  tarkista(await m.evaluate(() => document.getElementById('menuBtn').getAttribute('aria-expanded') === 'true' && document.activeElement.closest('#valikko') !== null), 'valikko avautuu näppäimistöllä ja kohdistus siirtyy siihen');
  await m.keyboard.press('Escape'); await m.waitForTimeout(200);
  tarkista(await kohdistus(m) === 'BUTTON#menuBtn.menu-toggle' && await m.evaluate(() => getComputedStyle(document.getElementById('valikko')).display === 'none'), 'Esc sulkee valikon ja palauttaa kohdistuksen painikkeeseen');
  for (const kieli of ['sv', 'en']) for (const w of [320, 375]) { await m.setViewportSize({ width: w, height: 700 }); await avaa(m, '#kieli=' + kieli + '&nakyma=analyysit');
    tarkista(await m.evaluate(() => document.documentElement.scrollWidth) <= w, `ei vaakavieritystä ${w} px leveydellä (${kieli})`); }
  await m.close();

  console.log('\nAnalyysien luvut');
  await avaa(s, '#nakyma=analyysit&vuosi=2025');
  const luvut = await s.evaluate(() => {
    const yi = S.year, e = Y.map(() => 0), nyt = new Set(), ennen = new Set();
    for (const r of R) { e[r[C.Y]] += r[C.SNT]; if (r[C.Y] === yi) nyt.add(r[C.S]); if (r[C.Y] === yi - 1) ennen.add(r[C.S]); }
    const num = t => +t.replace(/[^\d,-]/g, '').replace(',', '.').replace('−', '-');
    const vuosirivit = [...document.querySelectorAll('#aVuodet tbody tr')].map(tr => num(tr.children[1].textContent));
    const koko = [...document.querySelectorAll('#aKoko tbody tr')].reduce((x, tr) => [x[0] + num(tr.children[1].textContent), x[1] + num(tr.children[3].textContent)], [0, 0]);
    return { vuosiOk: vuosirivit.every((v, i) => Math.abs(v - Math.round(e[i] / 100)) <= 1), kokoN: koko[0], nyt: nyt.size, kokoE: koko[1], eur: Math.round(e[yi] / 100),
      uudet: +document.getElementById('aUudetSub').textContent.replace(/\s/g, '').match(/^\d+/)[0], uudetOik: [...nyt].filter(x => !ennen.has(x)).length,
      pois: +document.getElementById('aPoisSub').textContent.replace(/\s/g, '').match(/^\d+/)[0], poisOik: [...ennen].filter(x => !nyt.has(x)).length };
  });
  tarkista(luvut.vuosiOk, 'vuositaulukon summat vastaavat rivien summia');
  tarkista(luvut.kokoN === luvut.nyt && Math.abs(luvut.kokoE - luvut.eur) <= 5, 'kokoluokkien toimittajamäärä ja eurot täsmäävät vuoden kokonaislukuihin', JSON.stringify(luvut));
  tarkista(luvut.uudet === luvut.uudetOik && luvut.pois === luvut.poisOik, 'uusien ja poistuneiden toimittajien määrät täsmäävät', JSON.stringify(luvut));

  await selain.close();
  console.log(virheet ? `\n${virheet} tarkistusta epäonnistui.` : '\nKaikki tarkistukset menivät läpi.');
  process.exit(virheet ? 1 : 0);
})();
