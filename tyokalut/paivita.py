#!/usr/bin/env python3
"""
Paimion ostolaskudata – sivun päivitys.

Ajo:  python paivita.py
Vaatii: Python 3.9+, pandas, openpyxl, pillow  (pip install pandas openpyxl pillow)

Vaiheet:
 1. Lataa puuttuvat Excelit lahteet.json:n osoitteista kansioon lahdedata
 2. Lukee ja yhtenäistää vuosien sarakkeet
 3. Rikastaa toimittajat PRH:n YTJ-rajapinnasta (välimuisti prh_valimuisti.json)
 4. Hakee kunta–maakunta-luokituksen Tilastokeskukselta
 5. Kokoaa index.html repon juureen (data, kuntakartta, fontti ja kuva upotettuina)
"""
import base64, concurrent.futures as cf, io, json, re, sys, time, urllib.error, urllib.request
from datetime import date
from pathlib import Path
import numpy as np, pandas as pd
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # repon juuri: index.html ja README.md
SIVU = ROOT
# Lähdedata: repon juuressa (ei GitHubiin, ks. .gitignore) tai projektikansiossa sen vieressä
LAHDE = next((p for p in (ROOT / 'lahdedata', ROOT.parent / 'lahdedata') if p.exists()), ROOT / 'lahdedata')
UA = {'User-Agent': 'paimion-ostolaskudata-paivitys'}

def get(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()

# ---------- 1. lataus ----------
lahteet = {int(k): v for k, v in json.load(open(HERE / 'lahteet.json', encoding='utf-8')).items()}
VUODET = sorted(lahteet)
LAHDE.mkdir(exist_ok=True)
for y, url in lahteet.items():
    f = LAHDE / f'ostolaskut_{y}.xlsx'
    if not f.exists():
        print('Ladataan', y); f.write_bytes(get(url))

# ---------- 2. luku ja yhtenäistys ----------
def norm(c): return re.sub(r'[\s\-\.]', '', str(c)).lower()
MAP = {'tapahtumanumero':'tosite','tositenumero':'tosite','tapahtpvm':'pvm','tositepvä':'pvm',
       'tilinro':'tili','tilinumero':'tili','tilinnimi':'tilinimi','ytunnus':'ytunnus',
       'toimittaja':'toimittaja','toimittajannimi':'toimittaja','summa':'summa','summa(alv0%)':'summa',
       'toimielin':'toimielin','tulosalue':'tulosalue','toimittajanmaakoodi':'maa','palveluluokka':'palveluluokka'}
osat = []
for y in VUODET:
    f = LAHDE / f'ostolaskut_{y}.xlsx'
    raw = pd.read_excel(f, header=None)
    h = raw.index[raw.apply(lambda r: any(norm(v) in ('summa', 'summa(alv0%)') for v in r), axis=1)][0]
    df = pd.read_excel(f, header=h)
    df = df.rename(columns={c: MAP[norm(c)] for c in df.columns if norm(c) in MAP})
    df = df[[c for c in dict.fromkeys(MAP.values()) if c in df.columns]].copy()
    df['vuosi'] = y
    puuttuu = [c for c in ('toimittaja', 'ytunnus', 'summa', 'pvm', 'tili') if c not in df.columns]
    if puuttuu: sys.exit(f'Vuosi {y}: sarakkeita ei tunnistettu: {puuttuu}. Lisää nimet MAP-sanakirjaan.')
    print(f'{y}: {len(df)} riviä, {df.summa.sum():,.0f} €')
    osat.append(df)
d = pd.concat(osat, ignore_index=True)
d = d[d.summa.notna()].copy()
for c in ('toimielin', 'tulosalue', 'maa'):
    if c not in d.columns: d[c] = None
d['ytunnus'] = d.ytunnus.astype(str).str.strip().replace({'nan': None})
d['pvm'] = pd.to_datetime(d.pvm, errors='coerce')
for c in ['toimittaja', 'tilinimi', 'toimielin', 'tulosalue']:
    d[c] = d[c].astype(str).str.strip().replace({'nan': None, 'None': None})
d['tili'] = d.tili.astype(str).str.replace(r'\.0$', '', regex=True)
d['toimielin'] = d.toimielin.replace({'Tekninen ltk':'Tekninen lautakunta','Koulutusltk':'Koulutuslautakunta',
    'Keskusvaaliltk':'Keskusvaalilautakunta','Tarkastusltk':'Tarkastuslautakunta',
    'Sosiaali- ja terveysltk':'Sosiaali- ja terveyslautakunta','Sivistys- ja vapaa-aikaltk':'Sivistys- ja vapaa-aikalautakunta'})

# ---------- 3. PRH ----------
VM = HERE / 'prh_valimuisti.json'
cache = json.load(open(VM, encoding='utf-8')) if VM.exists() else {}
ids = sorted(set(i for i in d.ytunnus.dropna() if re.fullmatch(r'\d{7}-\d', i)))
todo = [i for i in ids if i not in cache]
print(f'PRH: {len(ids)} Y-tunnusta, haetaan {len(todo)} uutta')
def fi(x): return next((q['description'] for q in (x or {}).get('descriptions', []) if q['languageCode'] == '1'), None)
def prh(i):
    for a in range(6):
        try:
            j = json.loads(get(f'https://avoindata.prh.fi/opendata-ytj-api/v3/companies?businessId={i}', 30))
            c = j['companies'][0] if j.get('companies') else None
            if not c: return i, {}
            addr = sorted(c.get('addresses') or [], key=lambda a: a['type'])
            mc = next((p.get('municipalityCode') for a in addr for p in a.get('postOffices', []) if p.get('municipalityCode')), None)
            return i, {'kuntakoodi': mc, 'toimiala': fi(c.get('mainBusinessLine')),
                       'yhtiomuoto': fi(c['companyForms'][-1]) if c.get('companyForms') else None}
        except urllib.error.HTTPError as e:
            if e.code == 404: return i, {}
            time.sleep(2 * (a + 1))
        except Exception:
            time.sleep(2 * (a + 1))
    return i, None
with cf.ThreadPoolExecutor(6) as ex:
    for n, (i, v) in enumerate(ex.map(prh, todo)):
        if v is not None: cache[i] = v
        if n % 200 == 199: json.dump(cache, open(VM, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(cache, open(VM, 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- 4. kunnat ja maakunnat ----------
# Luokitusvuosi: päivitä, kun Tilastokeskus julkaisee uuden (esim. 20260101)
LUOKITUS = '20250101'
km = json.loads(get('https://data.stat.fi/api/classifications/v2/correspondenceTables/'
                    f'kunta_1_{LUOKITUS}%23maakunta_1_{LUOKITUS}/maps?content=data&meta=max&lang=fi&format=json'))
kn = {x['sourceItem']['code']: x['sourceItem']['classificationItemNames'][0]['name'] for x in km}
mk = {x['sourceItem']['code']: x['targetItem']['classificationItemNames'][0]['name'] for x in km}
name2code = {v: k for k, v in kn.items()}
GEN = {'turun':'Turku','liedon':'Lieto','kaarinan':'Kaarina','salon':'Salo','paraisten':'Parainen','raision':'Raisio','marttilan':'Marttila',
'helsingin':'Helsinki','naantalin':'Naantali','tampereen':'Tampere','sauvon':'Sauvo','ulvilan':'Ulvila','pöytyän':'Pöytyä','loimaan':'Loimaa',
'kuopion':'Kuopio','hyvinkään':'Hyvinkää','fossan':'Forssa','forssan':'Forssa','mynämäen':'Mynämäki','mikkelin':'Mikkeli','hangon':'Hanko','lahden':'Lahti',
'ylöjärven':'Ylöjärvi','äänekosken':'Äänekoski','jyväskylän':'Jyväskylä','maskun':'Masku','ruskon':'Rusko','sastamalan':'Sastamala','joensuun':'Joensuu',
'tyrnävän':'Tyrnävä','heinäveden':'Heinävesi','nousiaisten':'Nousiainen','uudenkaupungin':'Uusikaupunki','lohjan':'Lohja','hämeenlinnan':'Hämeenlinna',
'kemiönsaaren':'Kemiönsaari','laitilan':'Laitila','rovaniemen':'Rovaniemi','someron':'Somero','raaseporin':'Raasepori','ikaalisten':'Ikaalinen',
'parkanon':'Parkano','euran':'Eura','paimion':'Paimio','kouvolan':'Kouvola','espoon':'Espoo','vantaan':'Vantaa','oulun':'Oulu','porin':'Pori'}
# Käsin asetetut kotikunnat (ei YTJ-rajapinnassa)
MANUAL = {'0828255-9':'Turku','0204213-2':'Paimio','0136167-6':'Paimio','0922305-9':'Turku','3221065-1':'Turku','0823246-3':'Paimio',
          '1095237-1':'Turku','0246246-0':'Helsinki','0926151-4':'Helsinki','3222663-7':'Helsinki'}
PUB = r'kaupunki|kunta\b|kuntayhtymä|valtio|hyvinvointialue|seurakunta|virasto|poliisilaitos|hätäkeskuslaitos|kansaneläkelaitos|työterveyslaitos|ulosottolaitos|yliopisto|ely-keskus|valtiokonttori|varsinais-suomen liitto|valteri|kuntatyönantajat|hallinto-oikeus|taideyliopisto'
ORG = r'\bry\b|r\.y\.|yhdistys|liitto|säätiö|\bsr\b|seura\b|keskusjärjestö|perikunta|tiekunta|osakaskunta'
PUBFORM = {'Kunta','Kuntayhtymä','Valtion liikelaitos','Hyvinvointialue','Seurakunta','Valtio ja sen laitokset','Ev.lut.kirkko'}
ORGFORM = {'Aatteellinen yhdistys','Säätiö','Taloudellinen yhdistys','Uskonnollinen yhdyskunta','Muu yhdistys'}

d['ytunnus'] = d.ytunnus.fillna('')
d['skey'] = np.where(d.ytunnus != '', d.ytunnus, 'N:' + d.toimittaja.fillna('?'))
nimi = d.sort_values('vuosi').groupby('skey').toimittaja.agg(lambda s: s.iloc[-1])
maa = d.groupby('skey').maa.agg(lambda s: s.dropna().iloc[0] if s.notna().any() else None)
attr = {}
for k, n in nimi.items():
    nl = (n or '').lower(); e = cache.get(k) or {}
    kunta = kn.get(e.get('kuntakoodi')) if e else None
    if not kunta:
        kunta = MANUAL.get(k)
        if not kunta and re.search(r'kaupunki|kunta\b|seurakunta', nl): kunta = GEN.get(nl.split()[0] if nl else '')
    maak = mk.get(name2code.get(kunta)) if kunta else None
    form = e.get('yhtiomuoto')
    if form in PUBFORM or (form is None and re.search(PUB, nl)): om = 'Julkinen sektori'
    elif form in ORGFORM or (form is None and re.search(ORG, nl)): om = 'Järjestö tai säätiö'
    elif form: om = 'Yritys'
    elif re.search(r'\btmi\b|t:mi|toiminimi|\boy\b|\bab\b|\bky\b|gmbh|ltd|inc\b', nl): om = 'Yritys'
    else: om = 'Ei tiedossa'
    if not kunta and (maa.get(k) or 'FI') != 'FI': kunta = maak = 'Ulkomaat'
    tol = e.get('toimiala') or ('Julkinen sektori (ei toimialatietoa)' if om == 'Julkinen sektori' else
                                'Järjestö tai säätiö (ei toimialatietoa)' if om == 'Järjestö tai säätiö' else 'Ei tiedossa')
    attr[k] = dict(nimi=n, yt='' if k.startswith('N:') else k, kunta=kunta or 'Ei tiedossa', maakunta=maak or 'Ei tiedossa', toimiala=tol, omistus=om)
A = pd.DataFrame.from_dict(attr, orient='index')

# ---------- 5. data ja sivu ----------
d['tilil'] = d.tili + ' ' + d.tilinimi.fillna('')
sup = list(A.index); si = {k: i for i, k in enumerate(sup)}
dims = {}
def enc(vals):
    v = sorted(set(vals)); return v, {x: i for i, x in enumerate(v)}
for c in ['toimielin', 'tulosalue', 'tilil']:
    dims[c], idx = enc(d[c].fillna('–')); d[c + '_i'] = d[c].fillna('–').map(idx)
for c in ['kunta', 'maakunta', 'toimiala', 'omistus']:
    dims[c], _ = enc(A[c])
supattr = [[A.at[k, 'nimi'], A.at[k, 'yt'], dims['kunta'].index(A.at[k, 'kunta']), dims['maakunta'].index(A.at[k, 'maakunta']),
            dims['toimiala'].index(A.at[k, 'toimiala']), dims['omistus'].index(A.at[k, 'omistus'])] for k in sup]
ym = (d.pvm.dt.year * 100 + d.pvm.dt.month).fillna(0).astype(int)
tos = pd.to_numeric(d.tosite, errors='coerce').fillna(0).astype('int64')
R = np.column_stack([d.vuosi - VUODET[0], ym, d.skey.map(si), d.tilil_i, d.toimielin_i, d.tulosalue_i,
                     (d.summa * 100).round().astype('int64'), tos]).tolist()
data = dict(years=VUODET, dims=dims, sup=supattr, rows=R, built=f'{date.today().day}.{date.today().month}.{date.today().year}')

t = (HERE / 'template.html').read_text(encoding='utf-8')
im = Image.open(HERE / 'hero.jpg').convert('RGB'); b = io.BytesIO(); im.save(b, 'JPEG', quality=72, optimize=True, progressive=True)
dl = '\n        '.join(f'<a href="{lahteet[y]}">Ostolaskut {y}</a>' for y in VUODET)
out = (t.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
        .replace('__FONT__', base64.b64encode((HERE / 'rubik-latin.woff2').read_bytes()).decode())
        .replace('__HERO__', base64.b64encode(b.getvalue()).decode())
        .replace('__MAP__', (HERE / 'kartta.json').read_text(encoding='utf-8')).replace('__DOWNLOADS__', dl).replace('__YEARS__', f'{VUODET[0]}–{VUODET[-1]}'))
SIVU.mkdir(exist_ok=True)
(SIVU / 'index.html').write_text(out, encoding='utf-8')
print(f'Valmis: {SIVU / "index.html"} ({len(out.encode()) / 1e6:.1f} Mt)')
print(d.groupby('vuosi').summa.agg(['size', 'sum']).round(2).to_string())
