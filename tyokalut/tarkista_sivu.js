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
// Tarkistukset avaavat oletuksena yhteenvedon; sivun oma oletus (ohje) tarkistetaan erikseen
const avaa = async (sivu, hash = '') => { if (!hash.includes('nakyma=')) hash = hash ? hash + '&nakyma=yhteenveto' : '#nakyma=yhteenveto'; await sivu.goto('about:blank'); await sivu.goto(SIVU + hash); await sivu.waitForTimeout(700); };
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
    await avaa(sivu, '#nakyma=kehitys'); await axe(sivu, 'kehitys');
    await avaa(sivu, '#nakyma=kehitys&jako=tilil&vuosi=2020'); await axe(sivu, 'analyysit, ensimmäinen vuosi');
    await avaa(sivu); await sivu.click('#supTable .rowbtn'); await sivu.waitForTimeout(300); await axe(sivu, 'toimittajan ikkuna');
    tarkista(jsVirheet.length === 0, 'ei JavaScript-virheitä', jsVirheet.join('; '));
    tarkista(pyynnot.length === 0, 'sivu ei hae mitään verkosta', pyynnot.join(', '));
    await sivu.close();
  }

  console.log('\nKapea näyttö');
  for (const hash of ['', '#nakyma=kehitys', '#nakyma=toimittaja']) {
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
  await s.click('.seg.nak[data-nak="tili"] [data-v="t"]'); await s.focus('#tiliTable .rowbtn'); await s.keyboard.press('Enter'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => document.activeElement.getAttribute('aria-pressed')) === 'true', 'tilin valinta näppäimistöllä säilyttää kohdistuksen ja kertoo tilan');
  tarkista((await s.$eval('#live', e => e.textContent)).startsWith('Näkymä päivitetty'), 'ruudunlukijalle tilaviesti rajauksen jälkeen');
  await s.focus('#t-yhteenveto'); await s.keyboard.press('ArrowRight'); await s.waitForTimeout(300);
  tarkista(await kohdistus(s) === 'BUTTON#t-kehitys' && !(await s.evaluate(() => document.getElementById('p-kehitys').hidden)), 'välilehti vaihtuu nuolinäppäimellä');

  console.log('\nPysyvät linkit');
  await avaa(s, '#vuosi=2023&kunta=Paimio&tili=4340&nakyma=analyysit&jako=tilil&mittari_kunta=n&alue=fi');
  const tila = await s.evaluate(() => ({ vuosi: Y[S.year], kunta: D.kunta[S.kunta], tili: D.tilil[S.tilil], view: S.view, adim: S.adim, mittari: mode.kunta, alue: mode.zoom, hash: decodeURIComponent(location.hash) }));
  tarkista(tila.vuosi === 2023 && tila.kunta === 'Paimio' && tila.tili.startsWith('4340 ') && tila.view === 'kehitys' && tila.adim === 'tilil' && tila.mittari === 'n' && tila.alue === 'fi', 'osoitteen tila luetaan oikein', JSON.stringify(tila));
  tarkista(['vuosi=2023', 'kunta=Paimio', 'tili=4340', 'nakyma=kehitys', 'jako=tilil', 'mittari_kunta=n', 'alue=fi'].every(o => tila.hash.includes(o)), 'sama tila kirjoitetaan takaisin osoitteeseen', tila.hash);
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
      await avaa(k, `#kieli=${kieli}&nakyma=kehitys&vuosi=2024&tili=4340`); await axe(k, `${kieli}, analyysit ${leveys} px`);
    }
    await avaa(k); await k.click('#teema'); await k.waitForTimeout(300); await axe(k, `tumma ulkoasu, yhteenveto ${leveys} px`);
    await avaa(k, '#nakyma=kehitys&kunta=Paimio'); await axe(k, `tumma ulkoasu, analyysit ${leveys} px`);
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
  await avaa(k); tarkista(await k.evaluate(() => document.documentElement.dataset.teema === 'tumma' && getComputedStyle(document.body).backgroundColor !== 'rgb(245, 247, 251)'), 'ulkoasun valinta muistetaan selaimessa');
  await k.click('#teema'); await k.waitForTimeout(200);
  tarkista(await k.evaluate(() => !document.documentElement.dataset.teema && getComputedStyle(document.body).backgroundColor === 'rgb(245, 247, 251)'), 'paluu vaaleaan ulkoasuun');
  await k.setViewportSize({ width: 1400, height: 900 });
  await avaa(k, '#vuosi=2023&tili=4340'); await k.click('#valikko a[data-nakyma="ohje"]'); await k.waitForTimeout(300);
  const nav = await k.evaluate(() => ({ hash: location.hash, view: S.view, f: document.activeElement.id }));
  tarkista(nav.view === 'ohje' && nav.hash.includes('vuosi=2023') && nav.hash.includes('tili=4340') && nav.f === 't-ohje', 'yläpalkin linkki vaihtaa välilehden ja säilyttää rajaukset osoitteessa', JSON.stringify(nav));
  await k.close();
  const m = await selain.newPage({ viewport: { width: 375, height: 700 } });
  await avaa(m); await m.focus('#menuBtn'); await m.keyboard.press('Enter'); await m.waitForTimeout(200);
  tarkista(await m.evaluate(() => document.getElementById('menuBtn').getAttribute('aria-expanded') === 'true' && document.activeElement.closest('#valikko') !== null), 'valikko avautuu näppäimistöllä ja kohdistus siirtyy siihen');
  tarkista(await m.evaluate(() => ['ohje', 'yhteenveto', 'kehitys', 'toimittaja'].every(n => { const a = document.querySelector(`#valikko a[data-nakyma="${n}"]`); return a && a.getClientRects().length > 0; })), 'kapean näytön valikossa ovat kaikki näkymät');
  await m.click('#valikko a[data-nakyma="kehitys"]'); await m.waitForTimeout(300); tarkista(await m.evaluate(() => S.view === 'kehitys' && getComputedStyle(document.getElementById('valikko')).display === 'none'), 'valikon linkki avaa näkymän ja sulkee valikon'); await m.focus('#menuBtn'); await m.keyboard.press('Enter'); await m.waitForTimeout(200);
  await m.keyboard.press('Escape'); await m.waitForTimeout(200);
  tarkista(await kohdistus(m) === 'BUTTON#menuBtn.menu-toggle' && await m.evaluate(() => getComputedStyle(document.getElementById('valikko')).display === 'none'), 'Esc sulkee valikon ja palauttaa kohdistuksen painikkeeseen');
  for (const kieli of ['sv', 'en']) for (const w of [320, 375]) { await m.setViewportSize({ width: w, height: 700 }); await avaa(m, '#kieli=' + kieli + '&nakyma=kehitys');
    tarkista(await m.evaluate(() => document.documentElement.scrollWidth) <= w, `ei vaakavieritystä ${w} px leveydellä (${kieli})`); }
  await m.close();

  console.log('\nKehitys ja toimittaja');
  for (const leveys of LEVEYDET) {
    const t = await selain.newPage({ viewport: { width: leveys, height: 900 } });
    const virh = []; t.on('pageerror', e => virh.push(e.message));
    await avaa(t, '#nakyma=toimittaja'); await axe(t, `toimittajan haku ${leveys} px`);
    await t.fill('#supQ', 'oy'); await t.waitForTimeout(400); await t.click('#supRes .tulos'); await t.waitForTimeout(400); await axe(t, `toimittajan historia ${leveys} px`);
    tarkista(await t.evaluate(() => document.documentElement.scrollWidth) <= leveys, `toimittajan historia ei vieritä vaakaan ${leveys} px`);
    await t.click('#teema'); await t.waitForTimeout(300); await axe(t, `toimittajan historia, tumma ${leveys} px`);
    await avaa(t, '#nakyma=kehitys&kieli=en'); await axe(t, `kehitys, tumma, en ${leveys} px`); await t.click('#teema'); await t.click('#kielet [data-kieli="fi"]');
    tarkista(virh.length === 0, `ei JavaScript-virheitä (${leveys} px)`, virh.join('; '));
    await t.close();
  }
  await avaa(s, '#nakyma=analyysit&vuosi=2024'); tarkista(await s.evaluate(() => S.view === 'kehitys' && !document.getElementById('p-kehitys').hidden), 'vanha linkki nakyma=analyysit avaa Kehitys-välilehden');
  const kaaviot = await s.evaluate(() => ({ viivat: document.querySelectorAll('#kKaavio path').length, valitut: document.querySelectorAll('#aKeh input:checked').length, selite: document.querySelectorAll('#kSelite li').length,
    trendit: document.querySelectorAll('#aKeh .spark').length, rivit: document.querySelectorAll('#aKeh tbody tr').length, paik: document.querySelectorAll('#kPaikKaavio path').length, vaihto: document.querySelectorAll('#kVaihtKaavio path').length, nimi: document.querySelector('#kKaavio svg').getAttribute('aria-label') }));
  tarkista(kaaviot.viivat === 5 && kaaviot.valitut === 5 && kaaviot.selite === 5 && kaaviot.trendit === kaaviot.rivit && kaaviot.paik === 3 && kaaviot.vaihto === 2 && kaaviot.nimi.length > 40, 'kehityskaaviossa viisi suurinta, joka rivillä trendiviiva ja kaavioilla tekstivastine', JSON.stringify(kaaviot));
  await s.focus('#aKeh input:not(:checked)'); await s.keyboard.press('Space'); await s.waitForTimeout(300);
  const valinta = await s.evaluate(() => ({ viivat: document.querySelectorAll('#kKaavio path').length, f: document.activeElement.matches('#aKeh input:checked'), lukittu: document.querySelectorAll('#aKeh input:disabled').length, muut: document.querySelectorAll('#aKeh input:not(:checked)').length, tili: S.toimiala }));
  tarkista(valinta.viivat === 6 && valinta.f && valinta.lukittu === valinta.muut && valinta.tili === null, 'rivin lisäys kaavioon valintaruudulla: kuusi sarjaa, kohdistus säilyy, enempää ei voi valita eikä rivi rajaudu', JSON.stringify(valinta));
  const iso = await s.evaluate(() => { const e = SUP.map(() => 0); for (const r of R) e[r[C.S]] += r[C.SNT]; let b = -1; SUP.forEach((x, i) => { if (x[P.YT] && (b < 0 || e[i] > e[b])) b = i; }); return { yt: SUP[b][P.YT], nimi: SUP[b][P.NIMI], snt: e[b], rivit: R.filter(r => r[C.S] === b).length }; });
  await avaa(s, '#nakyma=toimittaja&toimittaja=' + iso.yt + '&vuosi=2021&tili=4340');
  const hist = await s.evaluate(() => { const num = t => +t.replace(/[^\d,-]/g, '').replace(',', '.');
    return { nimi: document.getElementById('tNimi').textContent, rajausPiilossa: document.getElementById('rajaus').hidden, summa: [...document.querySelectorAll('#tVuosiTaulu tbody tr')].reduce((x, tr) => x + (tr.children[1].textContent === '–' ? 0 : num(tr.children[1].textContent)), 0),
      otsikko: document.getElementById('tRivitH').textContent.replace(/\s/g, ''), kk: document.querySelectorAll('#tKk .col').length, hash: location.hash, sija: document.querySelector('#tVuosiTaulu tbody tr td:nth-child(4)').textContent }; });
  tarkista(hist.nimi === iso.nimi && hist.rajausPiilossa && Math.abs(hist.summa - iso.snt / 100) <= 6 && hist.otsikko.includes('(' + iso.rivit + ')') && hist.kk === 72 && /^\d+ \/ /.test(hist.sija), 'toimittajan historia: kaikki vuodet rajauksista riippumatta, summat ja rivimäärä täsmäävät', JSON.stringify(hist));
  tarkista(hist.hash.includes('nakyma=toimittaja') && hist.hash.includes('toimittaja=' + iso.yt), 'toimittajan historialla on pysyvä linkki', hist.hash);
  await avaa(s); await s.click('#supTable .rowbtn'); await s.waitForTimeout(300); await s.click('#dHist'); await s.waitForTimeout(400);
  tarkista(await s.evaluate(() => S.view === 'toimittaja' && S.sup !== null && !document.getElementById('drawer').classList.contains('open') && document.activeElement.id === 'tNimi' && !document.getElementById('sisalto').inert), 'pikakatselusta pääsee koko historiaan ja kohdistus siirtyy toimittajan nimeen');
  await s.focus('#t-toimittaja'); await s.keyboard.press('ArrowLeft'); await s.keyboard.press('ArrowLeft'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => S.view === 'yhteenveto' && !document.getElementById('rajaus').hidden), 'paluu yhteenvetoon tuo rajaukset takaisin');

  console.log('\nKaaviot ja listat');
  for (const leveys of LEVEYDET) {
    const c = await selain.newPage({ viewport: { width: leveys, height: 900 } });
    const virh = []; c.on('pageerror', e => virh.push(e.message));
    await avaa(c, '#kaavio=sup,tol,om,tili,ta,pl'); await axe(c, `kaavionäkymät ${leveys} px`);
    tarkista(await c.evaluate(() => document.documentElement.scrollWidth) <= leveys, `kaavionäkymät eivät vieritä vaakaan ${leveys} px`);
    await c.click('#teema'); await c.waitForTimeout(300); await axe(c, `kaavionäkymät, tumma ${leveys} px`); await c.click('#teema');
    await avaa(c, '#kaavio=sup,tol,om,tili,ta,pl,ryhma&kieli=sv&vuosi=2021'); await axe(c, `kaaviot ja tiliryhmätaulukko, sv ${leveys} px`); await c.click('#kielet [data-kieli="fi"]');
    tarkista(virh.length === 0, `ei JavaScript-virheitä (${leveys} px)`, virh.join('; '));
    await c.close();
  }
  await avaa(s, '#kaavio=sup');
  const kv = await s.evaluate(() => ({ t: document.getElementById('tiliT').hidden, k: document.getElementById('tiliK').hidden, laatat: document.querySelectorAll('#tiliK .tile').length, top: document.querySelectorAll('#supTop .hrow').length,
    ala: [...document.querySelectorAll('#tiliK .tile')].reduce((x, e) => x + parseFloat(e.style.width) * parseFloat(e.style.height), 0), versio: document.querySelector('#topbar .versio').textContent.replace(/\s+/g, ' ').trim(), rengas: document.querySelectorAll('#ryhmaK path').length }));
  tarkista(kv.t && !kv.k && kv.laatat >= 10 && kv.top === 11 && Math.abs(kv.ala - 10000) < 60 && kv.rengas >= 2, 'puukartta on oletuksena, linkin kaavio-parametri avaa kymmenen suurimman kaavion ja laatat täyttävät alueen', JSON.stringify(kv));
  tarkista(/v\d+\.\d+\.\d+/.test(kv.versio), 'versionumero näkyy yläpalkissa', kv.versio);
  await s.focus('#tiliK button.tile'); await s.keyboard.press('Enter'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => S.tilil !== null && document.activeElement.matches('#tiliK .tile[aria-pressed="true"]') && location.hash.includes('tili=') && location.hash.includes('kaavio=')), 'puukartan laatta rajaa näppäimistöllä, kohdistus säilyy ja valinta on osoitteessa');
  await s.click('.seg.nak[data-nak="tili"] [data-v="t"]'); await s.waitForTimeout(200);
  tarkista(await s.evaluate(() => !document.getElementById('tiliT').hidden && document.getElementById('tiliK').hidden && decodeURIComponent(location.hash).includes('kaavio=sup,tili')), 'esitystavan vaihto takaisin taulukkoon');
  await avaa(s, '#yhtiomuoto=Osakeyhtiö&vuosi=2024');
  tarkista(await s.evaluate(() => D.yhtiomuoto[S.yhtiomuoto] === 'Osakeyhtiö' && document.querySelectorAll('#supTable thead th').length === 6 && document.querySelector('#chips').textContent.includes('Osakeyhtiö')), 'yritysmuoto toimii rajauksena ja toimittajataulukossa on tyyppi ja toimiala');
  await avaa(s, '#nakyma=kehitys&vuosi=2024&raja=100000');
  const rj = await s.evaluate(() => { const e = new Map(); for (const r of R) if (r[C.Y] === S.year) e.set(r[C.S], (e.get(r[C.S]) || 0) + r[C.SNT]); const oik = [...e.values()].filter(v => v >= 100000 * 100).length;
    const te = new Map(); for (const r of R) if (r[C.Y] === S.year && D.toimielin[r[C.TE]] !== '–') { const k = r[C.S] + '|' + r[C.TILI]; if (!te.has(k)) te.set(k, new Set()); te.get(k).add(r[C.TE]); }
    return { n: +document.getElementById('aRajaSub').textContent.replace(/\s/g, '').match(/^\d+/)[0], oik, sama: +document.getElementById('aSamaSub').textContent.replace(/\s/g, '').match(/^\d+/)[0], samaOik: [...te.values()].filter(x => x.size >= 2).length, hash: location.hash }; });
  tarkista(rj.n === rj.oik && rj.sama === rj.samaOik && rj.hash.includes('raja=100000'), 'suurten toimittajien ja usean toimielimen tapausten määrät täsmäävät riveihin', JSON.stringify(rj));

  console.log('\nTaulukot ilman vaakavieritystä');
  const yt1 = iso.yt;
  for (const w of [1400, 1280, 1100, 900, 720, 375]) {
    const v = await selain.newPage({ viewport: { width: w, height: 900 } }); const ylit = [];
    for (const h of ['', '#kieli=sv', '#kaavio=tol,tili,ta,pl&kieli=sv', '#nakyma=kehitys', '#nakyma=kehitys&kieli=en&jako=tilil', '#nakyma=toimittaja&toimittaja=' + yt1, '#nakyma=toimittaja&kieli=sv&tvuosi=2023&toimittaja=' + yt1]) {
      await avaa(v, h); ylit.push(...await v.evaluate(() => [...document.querySelectorAll('.tblwrap')].filter(e => e.offsetParent && e.scrollWidth > e.clientWidth + 1).map(e => (e.querySelector('table').id || 'rivit') + ' +' + (e.scrollWidth - e.clientWidth))));
    }
    tarkista(ylit.length === 0, `taulukot mahtuvat ${w} px leveydelle`, ylit.join(', ')); await v.close();
  }
  await avaa(s, '#nakyma=toimittaja&toimittaja=' + yt1); await s.focus('#tVuodet .col[data-i="3"]'); await s.keyboard.press('Enter'); await s.waitForTimeout(300);
  const tv = await s.evaluate(() => ({ y: S.supYear, kk: document.querySelectorAll('#tKk .col').length, hash: location.hash, otsikko: document.getElementById('tRivitH').textContent, rivit: R.filter(r => r[C.S] === S.sup && r[C.Y] === 3).length, sel: document.getElementById('f-tvuosi').value }));
  tarkista(tv.y === 3 && tv.kk === 12 && tv.hash.includes('tvuosi=' + 2023) && tv.otsikko.replace(/\s/g, '').includes('2023(' + tv.rivit + ')') && tv.sel === '3', 'toimittajan historiasta voi valita vuoden: 12 kuukautta, vuoden laskurivit ja valinta osoitteessa', JSON.stringify(tv));
  await avaa(s); 
  tarkista(await s.evaluate(() => !document.getElementById('vinkki').hidden && document.querySelectorAll('#supTable .rowbtn .ri').length > 0 && document.querySelectorAll('#tiliTable .rowbtn .ri').length > 0 && document.querySelectorAll('#kunta .hrow .ri').length > 0), 'vinkki ja rivien kuvakkeet kertovat, mitä napsautus tekee');
  await s.click('#vinkkiSulje'); await avaa(s); tarkista(await s.evaluate(() => document.getElementById('vinkki').hidden), 'kuitattu vinkki pysyy piilossa');

  console.log('\nOhje');
  for (const leveys of [1280, 375, 320]) {
    const o = await selain.newPage({ viewport: { width: leveys, height: 900 } });
    for (const kieli of ['fi', 'sv', 'en']) { await avaa(o, '#nakyma=ohje&kieli=' + kieli); await axe(o, `ohje ${kieli} ${leveys} px`);
      tarkista(await o.evaluate(() => document.documentElement.scrollWidth) <= leveys && await o.evaluate(() => [...document.querySelectorAll('#p-ohje .opas')].every(e => e.textContent.length > 150) && document.getElementById('rajaus').hidden), `ohje ${kieli} ${leveys} px: sisältö näkyy eikä vieritä vaakaan`); }
    await o.click('#teema'); await o.waitForTimeout(200); await axe(o, `ohje, tumma ${leveys} px`); await o.click('#teema'); await o.click('#kielet [data-kieli="fi"]');
    await o.close();
  }
  await s.goto('about:blank'); await s.goto(SIVU); await s.waitForTimeout(600);
  tarkista(await s.evaluate(() => S.view === 'ohje' && !document.getElementById('p-ohje').hidden && document.getElementById('t-ohje').getAttribute('aria-selected') === 'true' && document.querySelector('#p-ohje .tervetuloa a.btn') !== null && document.querySelector('#palaute a[href^="mailto:"]') !== null && document.querySelector('#palaute a[href="https://summanen.org"]') !== null), 'sivu avautuu ohjeeseen, jossa on tervetuloteksti, ja Kysy ja ehdota -osiossa on yhteystiedot ja tekijän sivu');
  await s.goto('about:blank'); await s.goto(SIVU + '#vuosi=2023&tili=4340'); await s.waitForTimeout(600);
  tarkista(await s.evaluate(() => S.view === 'yhteenveto' && S.tilil !== null), 'vanha linkki ilman näkymää avaa yhteenvedon');
  await avaa(s, '#nakyma=ohje&vuosi=2022'); await s.click('#p-ohje .opas li a[data-nakyma="kehitys"]'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => S.view === 'kehitys' && location.hash.includes('vuosi=2022') && document.activeElement.id === 't-kehitys'), 'ohjeen linkki avaa näkymän ja säilyttää vuoden');

  console.log('\nSelaimen historia ja jakotiedot');
  const hst = await selain.newPage({ viewport: { width: 1280, height: 900 } });
  await avaa(hst, '#vuosi=2024'); await hst.click('.seg.nak[data-nak="tili"] [data-v="t"]'); await hst.click('#tiliTable .rowbtn'); await hst.waitForTimeout(300);
  await hst.click('#t-kehitys'); await hst.waitForTimeout(300);
  await hst.goBack(); await hst.waitForTimeout(400);
  const h1 = await hst.evaluate(() => ({ view: S.view, tili: S.tilil !== null, y: Y[S.year], siru: document.querySelectorAll('#chips .chip').length }));
  tarkista(h1.view === 'yhteenveto' && h1.tili && h1.y === 2024 && h1.siru === 1, 'Takaisin palauttaa edellisen välilehden ja säilyttää rajauksen', JSON.stringify(h1));
  await hst.goBack(); await hst.waitForTimeout(400);
  tarkista(await hst.evaluate(() => S.tilil === null && document.querySelectorAll('#chips .chip').length === 0 && document.documentElement.scrollWidth > 0), 'toinen Takaisin poistaa rajauksen');
  await hst.goForward(); await hst.waitForTimeout(400); tarkista(await hst.evaluate(() => S.tilil !== null), 'Eteenpäin palauttaa rajauksen');
  await hst.click('#supTable .rowbtn'); await hst.waitForTimeout(300); await hst.goBack(); await hst.waitForTimeout(400);
  tarkista(await hst.evaluate(() => !document.getElementById('drawer').classList.contains('open') && !document.getElementById('sisalto').inert && S.tilil !== null), 'Takaisin sulkee toimittajan ikkunan');
  const meta = await hst.evaluate(() => ({ kuvake: (document.querySelector('link[rel="icon"]') || {}).href || '', og: ['og:title', 'og:description', 'og:image', 'og:url'].every(p => (document.querySelector(`meta[property="${p}"]`) || {}).content), kuvaus: (document.querySelector('meta[name="description"]') || {}).content || '', ld: !!JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent).name }));
  tarkista(meta.kuvake.startsWith('data:image/svg+xml') && meta.og && meta.kuvaus.length > 80 && meta.ld && fs.existsSync(path.resolve(__dirname, '..', 'og-kuva.jpg')) && fs.existsSync(path.resolve(__dirname, '..', 'llms.txt')), 'sivukuvake, kuvaus, jakotiedot ja jakokuva ovat paikallaan', JSON.stringify(meta).slice(0, 200));
  await hst.close();
  await avaa(s, '#nakyma=toimittaja&tvuosi=2023&toimittaja=' + iso.yt); await s.click('#tKaikkiVuodet'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => S.supYear === null && !location.hash.includes('tvuosi') && document.querySelectorAll('#tKk .col').length === 72), 'toimittajan vuosivalinnan saa pois painikkeesta');
  await s.click('#supTyhjenna'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => S.sup === null && document.getElementById('supSivu').hidden && document.activeElement.id === 'supQ'), 'toimittajan voi vaihtaa ja kohdistus siirtyy hakuun');

  console.log('\nSivupalkki ja rajausikkuna');
  await avaa(s, '#vuosi=2024'); await s.selectOption('#f-toimiala', { index: 3 }); await s.waitForTimeout(300);
  const sp = await s.evaluate(() => ({ tol: S.toimiala !== null, siru: document.querySelectorAll('#chips .chip').length, valitut: !document.getElementById('valitut').hidden, hash: location.hash.includes('toimiala='), kiinni: getComputedStyle(document.getElementById('sivu')).position, hero: document.getElementById('hero').hidden && [...document.querySelectorAll('h1')].filter(e => e.getClientRects().length).length === 1, palkki: getComputedStyle(document.getElementById('rajaaPalkki')).display }));
  tarkista(sp.tol && sp.siru === 1 && sp.valitut && sp.hash && sp.kiinni === 'sticky' && sp.hero && sp.palkki === 'none', 'sivupalkin toimialavalikko rajaa, valinta näkyy kohdassa Valittuna ja sivupalkki pysyy näkyvissä', JSON.stringify(sp));
  await s.selectOption('#f-kunta2', { label: 'Paimio' }); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => D.kunta[S.kunta] === 'Paimio' && document.getElementById('f-kunta').value === document.getElementById('f-kunta2').value), 'sivupalkin ja kartan kuntavalikot pysyvät samassa arvossa');
  const rj2 = await selain.newPage({ viewport: { width: 375, height: 800 } });
  await avaa(rj2, '#kunta=Paimio');
  tarkista(await rj2.evaluate(() => getComputedStyle(document.getElementById('rajaimet')).display === 'none' && document.getElementById('rajaaAvaa').textContent.includes('(1)')), 'kapealla näytöllä rajaukset ovat piilossa ja painike kertoo rajausten määrän');
  await rj2.focus('#rajaaAvaa'); await rj2.keyboard.press('Enter'); await rj2.waitForTimeout(300); await axe(rj2, 'rajausikkuna auki 375 px');
  tarkista(await rj2.evaluate(() => document.getElementById('rajaimet').getAttribute('role') === 'dialog' && document.activeElement.id === 'rajaaSulje' && document.getElementById('sisalto').inert && document.documentElement.scrollWidth <= 375), 'rajausikkuna avautuu näppäimistöllä, kohdistus siirtyy siihen ja tausta ei ole käytettävissä');
  await rj2.selectOption('#f-toimielin', { index: 2 }); await rj2.waitForTimeout(300);
  tarkista(await rj2.evaluate(() => S.toimielin !== null && document.getElementById('rajaimet').classList.contains('open') && /\d/.test(document.getElementById('rajaaValmis').textContent)), 'rajaus ikkunassa päivittää näkymän ja ikkuna pysyy auki');
  await rj2.keyboard.press('Escape'); await rj2.waitForTimeout(300);
  tarkista(await rj2.evaluate(() => !document.getElementById('rajaimet').classList.contains('open') && document.activeElement.id === 'rajaaAvaa' && !document.getElementById('sisalto').inert && document.getElementById('rajaaAvaa').textContent.includes('(2)')), 'Esc sulkee rajausikkunan ja palauttaa kohdistuksen painikkeeseen');
  await rj2.selectOption('#f-vuosi', { label: '2022' }); await rj2.waitForTimeout(300);
  tarkista(await rj2.evaluate(() => Y[S.year] === 2022), 'vuoden voi vaihtaa kapealla näytöllä palkin valikosta');
  await rj2.click('#teema'); await rj2.click('#rajaaAvaa'); await rj2.waitForTimeout(300); await axe(rj2, 'rajausikkuna auki, tumma 375 px'); await rj2.keyboard.press('Escape'); await rj2.click('#teema');
  await rj2.close();

  await avaa(s, '#vuosi=2021&tili=4340&nakyma=kehitys'); await s.click('#alku'); await s.waitForTimeout(300);
  tarkista(await s.evaluate(() => S.view === 'ohje' && S.tilil === null && S.year === Y.length - 1 && document.getElementById('alku').textContent.includes('Paimion ostolaskudata') && document.getElementById('alku').getBoundingClientRect().left < 60), 'sivuston nimi on yläpalkin vasemmassa reunassa ja vie aloitukseen');
  for (const w of [1280, 375, 320]) { const b2 = await selain.newPage({ viewport: { width: w, height: 800 } }); for (const kieli of ['fi', 'sv', 'en']) { await avaa(b2, '#kieli=' + kieli);
      const y = await b2.evaluate(() => { const r = [...document.querySelectorAll('#topbar .wrap > *')].filter(e => e.offsetParent).map(e => e.getBoundingClientRect()); return { ulos: r.some(x => x.right > innerWidth + 1 || x.left < -1), paall: r.some((a, i) => r.some((b, j) => j > i && a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1)), sw: document.documentElement.scrollWidth }; });
      tarkista(!y.ulos && !y.paall && y.sw <= w, `yläpalkin osat mahtuvat eivätkä mene päällekkäin ${w} px (${kieli})`, JSON.stringify(y)); }
    await b2.click('#kielet [data-kieli="fi"]'); await b2.close(); }

  console.log('\nAnalyysien luvut');
  await avaa(s, '#nakyma=kehitys&vuosi=2025');
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
