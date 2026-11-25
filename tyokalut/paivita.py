#!/usr/bin/env python3
"""
Paimion ostolaskudata – sivun päivitys.

Ajo:    python tyokalut/paivita.py
Vaatii: Python 3.9+ ja requirements.txt:n kirjastot  (pip install -r requirements.txt)

Vaiheet:
 1. Etsii kaupungin Talous-sivulta uudet vuodet ja lataa puuttuvat Excelit kansioon lahdedata
 2. Lukee vuodet ja yhtenäistää sarakkeet
 3. Arvioi puuttuvat toimielimet ja tulosalueet palveluluokasta ja ajaa takautuvan testin
 4. Rikastaa toimittajat PRH:n YTJ-rajapinnasta (välimuisti prh_valimuisti.json)
 5. Hakee kunta–maakunta-luokituksen Tilastokeskukselta
 6. Kokoaa index.html:n repon juureen (data, kuntakartta, fontti ja kuva upotettuina)
"""
import base64
import concurrent.futures as cf
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

VERSIO = '1.5.1'                        # sivun versio; nosta samalla kun lisäät kohdan tiedostoon CHANGELOG.md

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # repon juuri: index.html ja README.md
# Lähdedata: repon juuressa (ei GitHubiin, ks. .gitignore) tai projektikansiossa sen vieressä
LAHDE = next((p for p in (ROOT / 'lahdedata', ROOT.parent / 'lahdedata') if p.exists()), ROOT / 'lahdedata')

TALOUS_SIVU = 'https://www.paimio.fi/kaupunki-ja-hallinto/talous/'
PRH_API = 'https://avoindata.prh.fi/opendata-ytj-api/v3/companies?businessId={}'
LUOKITUS = '20250101'                   # Tilastokeskuksen kuntaluokituksen vuosi; päivitä kuntaliitosten jälkeen
LUOKITUS_API = ('https://data.stat.fi/api/classifications/v2/correspondenceTables/'
                'kunta_1_{v}%23maakunta_1_{v}/maps?content=data&meta=max&lang=fi&format=json')
PALVELULUOKAT_API = ('https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/sbr-fi-code-lists/'
                     'codeschemes/PA-2024-2/codes/?format=json&pageSize=500')
UA = {'User-Agent': 'paimion-ostolaskudata-paivitys'}

ARVIO_KYNNYS = 0.8                      # arvio hyväksytään, jos vähintään tämä osuus euroista on samassa luokassa
ARVIO_OPETUSVUODET = 2                  # kuinka monesta edellisestä vuodesta vastaavuudet opitaan
ARVIO_AVAIMET = (['palveluluokka', 'tili', 'ytunnus'], ['palveluluokka', 'tili'], ['palveluluokka'])
PRH_VANHENEE_PV = 365                   # löytyneen yrityksen tiedot haetaan uudelleen tämän jälkeen
PRH_TYHJA_VANHENEE_PV = 90              # "ei löytynyt" yritetään uudelleen tämän jälkeen
PRH_HAETTU_OLETUS = '2026-09-23'        # välimuistin vanhat rivit, joilta hakupäivä puuttuu

# Sarakkeiden nimet eri vuosien tiedostoissa → yhtenäinen nimi. Avain: pienet kirjaimet, ei välejä, viivoja eikä pisteitä.
SARAKKEET = {
    'tapahtumanumero': 'tosite', 'tositenumero': 'tosite',
    'tapahtpvm': 'pvm', 'tositepvä': 'pvm',
    'tilinro': 'tili', 'tilinumero': 'tili', 'tilinnimi': 'tilinimi',
    'ytunnus': 'ytunnus',
    'toimittaja': 'toimittaja', 'toimittajannimi': 'toimittaja',
    'summa': 'summa', 'summa(alv0%)': 'summa',
    'toimielin': 'toimielin', 'tulosalue': 'tulosalue',
    'toimittajanmaakoodi': 'maa', 'palveluluokka': 'palveluluokka',
}
PAKOLLISET = ('toimittaja', 'ytunnus', 'summa', 'pvm', 'tili')
VALINNAISET = ('toimielin', 'tulosalue', 'maa', 'palveluluokka', 'tilinimi', 'tosite')
TOIMIELIN_NIMET = {
    'Tekninen ltk': 'Tekninen lautakunta', 'Koulutusltk': 'Koulutuslautakunta',
    'Keskusvaaliltk': 'Keskusvaalilautakunta', 'Tarkastusltk': 'Tarkastuslautakunta',
    'Sosiaali- ja terveysltk': 'Sosiaali- ja terveyslautakunta',
    'Sivistys- ja vapaa-aikaltk': 'Sivistys- ja vapaa-aikalautakunta',
}

# Toimittajat, joita ei ole PRH:n avoimessa rajapinnassa (kunnat, kuntayhtymät, yhdistykset, säätiöt):
# kotikunta päätellään nimen genetiivistä tai asetetaan käsin, tyyppi päätellään nimestä.
KUNTA_GENETIIVI = {
    'turun': 'Turku', 'liedon': 'Lieto', 'kaarinan': 'Kaarina', 'salon': 'Salo', 'paraisten': 'Parainen',
    'raision': 'Raisio', 'marttilan': 'Marttila', 'helsingin': 'Helsinki', 'naantalin': 'Naantali',
    'tampereen': 'Tampere', 'sauvon': 'Sauvo', 'ulvilan': 'Ulvila', 'pöytyän': 'Pöytyä', 'loimaan': 'Loimaa',
    'kuopion': 'Kuopio', 'hyvinkään': 'Hyvinkää', 'forssan': 'Forssa', 'mynämäen': 'Mynämäki',
    'fossan': 'Forssa',                 # kirjoitusvirhe kaupungin aineistossa ("Fossan kaupunki")
    'mikkelin': 'Mikkeli', 'hangon': 'Hanko', 'lahden': 'Lahti', 'ylöjärven': 'Ylöjärvi',
    'äänekosken': 'Äänekoski', 'jyväskylän': 'Jyväskylä', 'maskun': 'Masku', 'ruskon': 'Rusko',
    'sastamalan': 'Sastamala', 'joensuun': 'Joensuu', 'tyrnävän': 'Tyrnävä', 'heinäveden': 'Heinävesi',
    'nousiaisten': 'Nousiainen', 'uudenkaupungin': 'Uusikaupunki', 'lohjan': 'Lohja',
    'hämeenlinnan': 'Hämeenlinna', 'kemiönsaaren': 'Kemiönsaari', 'laitilan': 'Laitila',
    'rovaniemen': 'Rovaniemi', 'someron': 'Somero', 'raaseporin': 'Raasepori', 'ikaalisten': 'Ikaalinen',
    'parkanon': 'Parkano', 'euran': 'Eura', 'paimion': 'Paimio', 'kouvolan': 'Kouvola', 'espoon': 'Espoo',
    'vantaan': 'Vantaa', 'oulun': 'Oulu', 'porin': 'Pori',
}
KUNTA_KASIN = {
    '0828255-9': 'Turku', '0204213-2': 'Paimio', '0136167-6': 'Paimio', '0922305-9': 'Turku',
    '3221065-1': 'Turku', '0823246-3': 'Paimio', '1095237-1': 'Turku', '0246246-0': 'Helsinki',
    '0926151-4': 'Helsinki', '3222663-7': 'Helsinki',
}
RE_KUNTANIMI = r'kaupunki|kunta\b|seurakunta'
RE_JULKINEN = (r'kaupunki|kunta\b|kuntayhtymä|valtio|hyvinvointialue|seurakunta|virasto|poliisilaitos|'
               r'hätäkeskuslaitos|kansaneläkelaitos|työterveyslaitos|ulosottolaitos|yliopisto|ely-keskus|'
               r'valtiokonttori|varsinais-suomen liitto|valteri|kuntatyönantajat|hallinto-oikeus|taideyliopisto')
RE_JARJESTO = r'\bry\b|r\.y\.|yhdistys|liitto|säätiö|\bsr\b|seura\b|keskusjärjestö|perikunta|tiekunta|osakaskunta'
RE_YRITYS = r'\btmi\b|t:mi|toiminimi|\boy\b|\bab\b|\bky\b|gmbh|ltd|inc\b'
MUOTO_JULKINEN = {'Kunta', 'Kuntayhtymä', 'Valtion liikelaitos', 'Hyvinvointialue', 'Seurakunta',
                  'Valtio ja sen laitokset', 'Ev.lut.kirkko'}
MUOTO_JARJESTO = {'Aatteellinen yhdistys', 'Säätiö', 'Taloudellinen yhdistys', 'Uskonnollinen yhdyskunta',
                  'Muu yhdistys'}
EI_TIEDOSSA = 'Ei tiedossa'


def hae(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def lue_json(polku, oletus=None):
    return json.loads(polku.read_text(encoding='utf-8')) if polku.exists() else oletus


def kirjoita_json(polku, data, **kw):
    """Kirjoittaa väliaikaistiedoston kautta, jottei keskeytys jätä puolikasta tiedostoa."""
    tmp = polku.with_suffix(polku.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, **kw), encoding='utf-8', newline='\n')
    tmp.replace(polku)


# ---------- 1. lähteet ----------
def etsi_uudet_lahteet(lahteet, html=None):
    """Lisää lahteet-sanakirjaan Talous-sivulta löytyvät vuodet, joita siinä ei vielä ole. Palauttaa lisätyt vuodet."""
    if html is None:
        html = hae(TALOUS_SIVU).decode('utf-8', 'replace')
    uudet = []
    for url, vuosi in re.findall(r'href="(https://www\.paimio\.fi/uploads/[^"]*?ostolaskut[-_]vuodelta[-_](\d{4})\.xlsx)"', html, re.I):
        if int(vuosi) not in lahteet:
            lahteet[int(vuosi)] = url
            uudet.append(int(vuosi))
    return sorted(uudet)


def lataa_lahteet():
    polku = HERE / 'lahteet.json'
    lahteet = {int(k): v for k, v in lue_json(polku).items()}
    try:
        uudet = etsi_uudet_lahteet(lahteet)
        if uudet:
            print(f'Uusia vuosia kaupungin sivulla: {uudet} – lisätty tiedostoon lahteet.json')
            kirjoita_json(polku, {str(k): lahteet[k] for k in sorted(lahteet)}, indent=2)
    except Exception as e:                                  # verkko poikki tms.: jatketaan tunnetuilla vuosilla
        print(f'Uusien vuosien tarkistus ei onnistunut ({e}); jatketaan tiedoston lahteet.json vuosilla')
    LAHDE.mkdir(exist_ok=True)
    for vuosi, url in sorted(lahteet.items()):
        f = LAHDE / f'ostolaskut_{vuosi}.xlsx'
        if not f.exists():
            print('Ladataan', vuosi)
            f.write_bytes(hae(url))
    return lahteet


# ---------- 2. luku ja yhtenäistys ----------
def normalisoi(nimi):
    return re.sub(r'[\s\-\.]', '', str(nimi)).lower()


def yhtenaista(raaka, vuosi):
    """Raakataulukko ilman otsikkoriviä → yhtenäiset sarakkeet. Otsikkorivi tunnistetaan Summa-sarakkeesta."""
    otsikko = next((i for i, rivi in enumerate(raaka.itertuples(index=False))
                    if any(SARAKKEET.get(normalisoi(v)) == 'summa' for v in rivi)), None)
    if otsikko is None:
        sys.exit(f'Vuosi {vuosi}: otsikkoriviä ei löytynyt (Summa-sarake puuttuu).')
    df = raaka.iloc[otsikko + 1:].copy()
    df.columns = [SARAKKEET.get(normalisoi(c), f'_{i}') for i, c in enumerate(raaka.iloc[otsikko])]
    df = df[[c for c in dict.fromkeys(SARAKKEET.values()) if c in df.columns]]
    puuttuu = [c for c in PAKOLLISET if c not in df.columns]
    if puuttuu:
        sys.exit(f'Vuosi {vuosi}: sarakkeita ei tunnistettu: {puuttuu}. Lisää nimet SARAKKEET-sanakirjaan.')
    for c in VALINNAISET:
        if c not in df.columns:
            df[c] = None
    df['summa'] = pd.to_numeric(df.summa, errors='coerce')
    df = df[df.summa.notna()].copy()
    df['vuosi'] = vuosi
    df['pvm'] = pd.to_datetime(df.pvm, errors='coerce')
    for c in ('ytunnus', 'toimittaja', 'tilinimi', 'toimielin', 'tulosalue', 'palveluluokka', 'maa'):
        df[c] = df[c].astype(str).str.strip().replace({'nan': None, 'None': None, '': None})
    df['tili'] = df.tili.astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    df['toimielin'] = df.toimielin.replace(TOIMIELIN_NIMET)
    return df.reset_index(drop=True)


def lue_vuodet(vuodet):
    osat = []
    for vuosi in vuodet:
        df = yhtenaista(pd.read_excel(LAHDE / f'ostolaskut_{vuosi}.xlsx', header=None), vuosi)
        print(f'{vuosi}: {len(df)} riviä, {df.summa.sum():,.2f} €')
        osat.append(df)
    return pd.concat(osat, ignore_index=True)


# ---------- 3. puuttuvien toimielinten ja tulosalueiden arviointi ----------
def ennusta(opetus, kohde, sarake):
    """Arvioi sarakkeen (toimielin/tulosalue) kohderiveille opetusrivien perusteella.

    Tarkin täsmäävä avain voittaa: (palveluluokka, tili, Y-tunnus) → (palveluluokka, tili) → palveluluokka.
    Avaimelle annetaan arvio vain, jos vähintään ARVIO_KYNNYS sen euroista kuuluu samaan luokkaan.
    Palauttaa sarjan, jossa arvioimatta jääneet ovat NaN.
    """
    tulos = pd.Series(index=kohde.index, dtype=object)
    opetus = opetus.assign(ytunnus=opetus.ytunnus.fillna(''), eur=opetus.summa.abs())
    kohde = kohde.assign(ytunnus=kohde.ytunnus.fillna(''))
    for avaimet in ARVIO_AVAIMET:
        g = opetus.groupby(avaimet + [sarake], as_index=False).eur.sum()
        g['osuus'] = g.eur / g.groupby(avaimet).eur.transform('sum')
        paras = g.sort_values('osuus').groupby(avaimet).tail(1)
        paras = paras[paras.osuus >= ARVIO_KYNNYS][avaimet + [sarake]]
        auki = kohde[tulos.isna()]
        osuma = auki[avaimet].merge(paras, on=avaimet, how='left')[sarake]
        osuma.index = auki.index
        tulos.update(osuma.dropna())
    return tulos


def arvioi_puuttuvat(d):
    """Täyttää puuttuvat toimielimet ja tulosalueet. Lisää sarakkeen arvio (1 = vähintään toinen arvioitu)."""
    d['arvio'] = 0
    yhteenveto = {}
    for sarake in ('toimielin', 'tulosalue'):
        tiedossa = d[d[sarake].notna() & d.palveluluokka.notna()]      # vain kaupungin oma tieto kelpaa opetukseen
        puuttuu = d[d[sarake].isna() & d.palveluluokka.notna()]
        for vuosi in sorted(puuttuu.vuosi.unique()):
            # vain edelliset vuodet, jotta organisaatiomuutokset (esim. sote-siirto 2023) eivät vääristä
            vuodet = sorted(tiedossa[tiedossa.vuosi < vuosi].vuosi.unique())[-ARVIO_OPETUSVUODET:]
            if not vuodet:
                continue
            kohde = puuttuu[puuttuu.vuosi == vuosi]
            arvio = ennusta(tiedossa[tiedossa.vuosi.isin(vuodet)], kohde, sarake).dropna()
            d.loc[arvio.index, sarake] = arvio
            d.loc[arvio.index, 'arvio'] = 1
            kattavuus = kohde.loc[arvio.index, 'summa'].abs().sum() / kohde.summa.abs().sum()
            yhteenveto.setdefault(sarake, {})[int(vuosi)] = {
                'opetusvuodet': [int(v) for v in vuodet], 'kattavuus': round(float(kattavuus), 4)}
            print(f'Arvioitu {sarake} {vuosi}: {len(arvio)}/{len(kohde)} riviä, {kattavuus:.0%} euroista '
                  f'(opetus {vuodet[0]}–{vuodet[-1]})')
    return yhteenveto


def takautuva_testi(d):
    """Sama menetelmä vuotta aiemmin: viimeisin vuosi, jolta oikea tieto on, arvioidaan sitä edeltävistä vuosista.

    Ajetaan alkuperäiselle datalle ennen arviointia. Palauttaa euroilla painotetun kattavuuden ja osuvuuden.
    """
    tulos = {}
    for sarake in ('toimielin', 'tulosalue'):
        tiedossa = d[d[sarake].notna() & d.palveluluokka.notna()]
        vuodet = sorted(tiedossa.vuosi.unique())
        if len(vuodet) < 2:
            continue
        testivuosi = vuodet[-1]
        opetusvuodet = vuodet[:-1][-ARVIO_OPETUSVUODET:]
        testi = tiedossa[tiedossa.vuosi == testivuosi]
        arvio = ennusta(tiedossa[tiedossa.vuosi.isin(opetusvuodet)], testi, sarake)
        eur = testi.summa.abs()
        arvioitu = arvio.notna()
        tulos[sarake] = {
            'testivuosi': int(testivuosi), 'opetusvuodet': [int(v) for v in opetusvuodet],
            'kattavuus': round(float(eur[arvioitu].sum() / eur.sum()), 4),
            'osuvuus': round(float(eur[arvioitu & (arvio == testi[sarake])].sum() / eur[arvioitu].sum()), 4),
        }
        print(f'Takautuva testi, {sarake}: vuosi {testivuosi} arvioitu vuosista {opetusvuodet[0]}–{opetusvuodet[-1]}: '
              f'osuvuus {tulos[sarake]["osuvuus"]:.1%}, kattavuus {tulos[sarake]["kattavuus"]:.1%} euroista')
    return tulos


# ---------- 4. PRH ----------
def _fi(kohde):
    return next((q['description'] for q in (kohde or {}).get('descriptions', []) if q['languageCode'] == '1'), None)


def prh_hae(ytunnus):
    """Palauttaa yrityksen tiedot, {} jos yritystä ei ole rajapinnassa, tai None jos haku epäonnistui."""
    for yritys in range(6):
        try:
            vastaus = json.loads(hae(PRH_API.format(ytunnus), 30))
            c = vastaus['companies'][0] if vastaus.get('companies') else None
            if not c:
                return {}
            osoitteet = sorted(c.get('addresses') or [], key=lambda a: a['type'])      # käyntiosoite ensin
            kunta = next((p.get('municipalityCode') for a in osoitteet for p in a.get('postOffices', [])
                          if p.get('municipalityCode')), None)
            return {'kuntakoodi': kunta, 'toimiala': _fi(c.get('mainBusinessLine')),
                    'yhtiomuoto': _fi(c['companyForms'][-1]) if c.get('companyForms') else None}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}
            time.sleep(2 * (yritys + 1))
        except Exception:
            time.sleep(2 * (yritys + 1))
    return None


def prh_vanhentuneet(valimuisti, ytunnukset, tanaan):
    """Y-tunnukset, joita ei ole välimuistissa tai joiden tieto on vanhentunut."""
    haettavat = []
    for yt in ytunnukset:
        rivi = valimuisti.get(yt)
        if rivi is None:
            haettavat.append(yt)
            continue
        ika = (tanaan - date.fromisoformat(rivi.get('haettu', PRH_HAETTU_OLETUS))).days
        tyhja = not any(v for k, v in rivi.items() if k != 'haettu')
        if ika > (PRH_TYHJA_VANHENEE_PV if tyhja else PRH_VANHENEE_PV):
            haettavat.append(yt)
    return haettavat


def paivita_prh(d):
    polku = HERE / 'prh_valimuisti.json'
    valimuisti = lue_json(polku, {})
    for rivi in valimuisti.values():
        rivi.setdefault('haettu', PRH_HAETTU_OLETUS)
    tanaan = date.today()
    ytunnukset = sorted({y for y in d.ytunnus.dropna() if re.fullmatch(r'\d{7}-\d', y)})
    haettavat = prh_vanhentuneet(valimuisti, ytunnukset, tanaan)
    print(f'PRH: {len(ytunnukset)} Y-tunnusta, haetaan {len(haettavat)} uutta tai vanhentunutta')
    epaonnistui = 0
    with cf.ThreadPoolExecutor(6) as ex:
        for n, (yt, tiedot) in enumerate(zip(haettavat, ex.map(prh_hae, haettavat))):
            if tiedot is None:                              # vanha tieto säilyy, yritetään seuraavalla ajolla
                epaonnistui += 1
                continue
            valimuisti[yt] = {**tiedot, 'haettu': tanaan.isoformat()}
            if n % 200 == 199:
                kirjoita_json(polku, valimuisti)
    kirjoita_json(polku, valimuisti)
    if epaonnistui:
        print(f'PRH: {epaonnistui} hakua epäonnistui, yritetään seuraavalla ajolla')
    return valimuisti


# ---------- 5. luokitukset ----------
def kuntaluokitus():
    """Palauttaa (kuntakoodi → kunnan nimi, kunnan nimi → maakunta)."""
    parit = json.loads(hae(LUOKITUS_API.format(v=LUOKITUS)))
    nimi = lambda kohde: kohde['classificationItemNames'][0]['name']
    koodi_nimi = {x['sourceItem']['code']: nimi(x['sourceItem']) for x in parit}
    kunta_maakunta = {nimi(x['sourceItem']): nimi(x['targetItem']) for x in parit}
    return koodi_nimi, kunta_maakunta


def palveluluokat():
    """Palveluluokan koodi → nimi (Valtiokonttorin koodisto). Tallennetaan tiedostoon palveluluokat.json."""
    polku = HERE / 'palveluluokat.json'
    nimet = lue_json(polku)
    if nimet is None:
        vastaus = json.loads(hae(PALVELULUOKAT_API))
        nimet = {c['codeValue']: c['prefLabel'].get('fi') for c in vastaus.get('results', vastaus)
                 if c.get('prefLabel', {}).get('fi')}
        kirjoita_json(polku, dict(sorted(nimet.items())), indent=1)
    return nimet


def palveluluokan_nimi(koodi, nimet):
    """'3051' → '3051 Perusopetus'; kaupungin oma I-alkuinen koodi → '… (I-koodi)'; tuntematon → koodi."""
    if koodi in nimet:
        return f'{koodi} {nimet[koodi]}'
    if koodi.startswith('I') and koodi[1:] in nimet:
        return f'{koodi} {nimet[koodi[1:]]} (I-koodi)'
    return koodi


# ---------- toimittajien luokittelu ----------
def paattele_kunta(ytunnus, nimi, prh, koodi_nimi):
    kunta = koodi_nimi.get((prh or {}).get('kuntakoodi'))
    if kunta:
        return kunta
    if ytunnus in KUNTA_KASIN:
        return KUNTA_KASIN[ytunnus]
    pienella = (nimi or '').lower()
    if pienella and re.search(RE_KUNTANIMI, pienella):
        return KUNTA_GENETIIVI.get(pienella.split()[0])
    return None


def paattele_tyyppi(nimi, yhtiomuoto):
    pienella = (nimi or '').lower()
    if yhtiomuoto in MUOTO_JULKINEN or (yhtiomuoto is None and re.search(RE_JULKINEN, pienella)):
        return 'Julkinen sektori'
    if yhtiomuoto in MUOTO_JARJESTO or (yhtiomuoto is None and re.search(RE_JARJESTO, pienella)):
        return 'Järjestö tai säätiö'
    if yhtiomuoto or re.search(RE_YRITYS, pienella):
        return 'Yritys'
    return EI_TIEDOSSA


def luokittele_toimittajat(d, valimuisti, koodi_nimi, kunta_maakunta):
    """Yksi rivi toimittajaa kohden. Toimittaja tunnistetaan Y-tunnuksella, sen puuttuessa nimellä."""
    d['avain'] = np.where(d.ytunnus.notna(), d.ytunnus, 'N:' + d.toimittaja.fillna('?'))
    nimet = d.sort_values('vuosi', kind='stable').groupby('avain').toimittaja.last()
    maat = d.groupby('avain').maa.first()
    eurot = d.groupby('avain').summa.sum()
    rivit = {}
    for avain, nimi in nimet.items():
        ytunnus = '' if avain.startswith('N:') else avain
        prh = valimuisti.get(avain) or {}
        kunta = paattele_kunta(ytunnus, nimi, prh, koodi_nimi)
        maakunta = kunta_maakunta.get(kunta)
        maa = maat.get(avain)
        if not kunta and pd.notna(maa) and maa != 'FI':     # maakoodi on aineistossa vasta vuodesta 2022
            kunta = maakunta = 'Ulkomaat'
        tyyppi = paattele_tyyppi(nimi, prh.get('yhtiomuoto'))
        toimiala = prh.get('toimiala') or (
            f'{tyyppi} (ei toimialatietoa)' if tyyppi in ('Julkinen sektori', 'Järjestö tai säätiö') else EI_TIEDOSSA)
        rivit[avain] = dict(nimi=nimi, yt=ytunnus, kunta=kunta or EI_TIEDOSSA, maakunta=maakunta or EI_TIEDOSSA,
                            toimiala=toimiala, omistus=tyyppi, eur=round(float(eurot[avain]), 2))
    return pd.DataFrame.from_dict(rivit, orient='index')


def kirjoita_tunnistamattomat(toimittajat):
    """Lista toimittajista, joiden kunta tai tyyppi jäi tunnistamatta, suurimmasta alkaen. Tarkista uudet rivit käsin."""
    t = toimittajat[(toimittajat.kunta == EI_TIEDOSSA) | (toimittajat.omistus == EI_TIEDOSSA)]
    t = t.assign(itseis=t.eur.abs()).sort_values('itseis', ascending=False)
    with open(HERE / 'tunnistamattomat.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['ytunnus', 'nimi', 'eurot_yhteensa', 'kunta', 'tyyppi'])
        for _, r in t.iterrows():
            w.writerow([r.yt, r.nimi, f'{r.eur:.2f}', r.kunta, r.omistus])
    osuus = t.itseis.sum() / toimittajat.eur.abs().sum()
    print(f'Tunnistamatta {len(t)} toimittajaa ({osuus:.1%} euroista), ks. tunnistamattomat.csv')


# ---------- 6. sivun kokoaminen ----------
# Rivin sarakkeet sivun datassa; samat vakiot on tiedoston template.html alussa (const C).
RIVI = ('vuosi', 'kuukausi', 'toimittaja', 'tili', 'toimielin', 'tulosalue', 'sentit', 'tosite', 'arvio', 'palveluluokka')


def kokoa_data(d, toimittajat, vuodet, pl_nimet, testi, arviot):
    d = d.copy()
    d['tilil'] = d.tili + ' ' + d.tilinimi.fillna('')
    d['pl'] = d.palveluluokka.map(lambda k: palveluluokan_nimi(k, pl_nimet), na_action='ignore')
    dims, indeksi = {}, {}
    for sarake, nimi in (('toimielin', 'toimielin'), ('tulosalue', 'tulosalue'), ('tilil', 'tilil'), ('pl', 'palveluluokka')):
        arvot = sorted(set(d[sarake].fillna('–')))
        dims[nimi] = arvot
        indeksi[nimi] = d[sarake].fillna('–').map({a: i for i, a in enumerate(arvot)})
    for sarake in ('kunta', 'maakunta', 'toimiala', 'omistus'):
        dims[sarake] = sorted(set(toimittajat[sarake]))
    paikka = {s: {a: i for i, a in enumerate(dims[s])} for s in ('kunta', 'maakunta', 'toimiala', 'omistus')}
    avaimet = list(toimittajat.index)
    sup = [[t.nimi, t.yt, paikka['kunta'][t.kunta], paikka['maakunta'][t.maakunta],
            paikka['toimiala'][t.toimiala], paikka['omistus'][t.omistus]] for t in toimittajat.itertuples()]
    rivit = np.column_stack([
        d.vuosi - vuodet[0],
        (d.pvm.dt.year * 100 + d.pvm.dt.month).fillna(0).astype(int),
        d.avain.map({a: i for i, a in enumerate(avaimet)}),
        indeksi['tilil'], indeksi['toimielin'], indeksi['tulosalue'],
        (d.summa * 100).round().astype('int64'),
        pd.to_numeric(d.tosite, errors='coerce').fillna(0).astype('int64'),
        d.arvio, indeksi['palveluluokka'],
    ]).tolist()
    assert len(rivit[0]) == len(RIVI)
    tanaan = date.today()
    return dict(years=vuodet, dims=dims, sup=sup, rows=rivit, backtest=testi, arviot=arviot,
                kynnys=ARVIO_KYNNYS, built=f'{tanaan.day}.{tanaan.month}.{tanaan.year}')


def kokoa_sivu(data, lahteet, vuodet):
    b64 = lambda nimi: base64.b64encode((HERE / nimi).read_bytes()).decode()
    lataukset = '\n        '.join(f'<a href="{lahteet[v]}">Ostolaskut {v}</a>' for v in vuodet)
    # "</" katkaisisi script-elementin, jos se sattuisi toimittajan nimeen
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    sivu = (HERE / 'template.html').read_text(encoding='utf-8')
    for merkki, arvo in (('__DATA__', data_json), ('__MAP__', (HERE / 'kartta.json').read_text(encoding='utf-8')),
                         ('__FONT__', b64('rubik-latin.woff2')), ('__HERO__', b64('hero.svg')),
                         ('__DOWNLOADS__', lataukset), ('__YEARS__', f'{vuodet[0]}–{vuodet[-1]}'),
                         ('__VERSION__', VERSIO)):
        if merkki not in sivu:
            sys.exit(f'template.html: paikkamerkki {merkki} puuttuu')
        sivu = sivu.replace(merkki, arvo)
    (ROOT / 'index.html').write_text(sivu, encoding='utf-8', newline='\n')
    return len(sivu.encode()) / 1e6


def main():
    lahteet = lataa_lahteet()
    vuodet = sorted(lahteet)
    d = lue_vuodet(vuodet)
    testi = takautuva_testi(d)
    arviot = arvioi_puuttuvat(d)
    valimuisti = paivita_prh(d)
    koodi_nimi, kunta_maakunta = kuntaluokitus()
    toimittajat = luokittele_toimittajat(d, valimuisti, koodi_nimi, kunta_maakunta)
    kirjoita_tunnistamattomat(toimittajat)
    data = kokoa_data(d, toimittajat, vuodet, palveluluokat(), testi, arviot)
    koko = kokoa_sivu(data, lahteet, vuodet)
    print(f'Valmis: {ROOT / "index.html"} ({koko:.1f} Mt)')


if __name__ == '__main__':
    main()
