"""
Testit päivitysskriptille.  Ajo repon juuressa:  python -m pytest tyokalut

Osa testeistä käyttää kaupungin Excel-tiedostoja ja valmista index.html:ää; ne ohitetaan, jos tiedostoja ei ole.
"""
import json
import re
from datetime import date

import pandas as pd
import pytest

import paivita as p


# ---------- sarakkeiden yhtenäistys ----------
def test_yhtenaista_loytaa_otsikkorivin_ja_nimeaa_sarakkeet():
    raaka = pd.DataFrame([
        [577, 'Paimion kaupunki', None, None, None, None],
        ['Tapaht.pvm', 'Tili-nro', 'Y-tunnus', 'Toimittaja', 'Summa', 'Toimielin'],
        ['2020-01-15', 4350.0, '1234567-8', ' Firma Oy ', 100.5, 'Tekninen ltk'],
        ['2020-02-01', 4360, None, 'Toinen', None, None],          # ei summaa → pudotetaan
    ])
    df = p.yhtenaista(raaka, 2020)
    assert len(df) == 1
    rivi = df.iloc[0]
    assert (rivi.tili, rivi.toimittaja, rivi.summa, rivi.vuosi) == ('4350', 'Firma Oy', 100.5, 2020)
    assert rivi.toimielin == 'Tekninen lautakunta'
    assert rivi.pvm == pd.Timestamp('2020-01-15')
    assert pd.isna(rivi.palveluluokka) and pd.isna(rivi.tulosalue)


def test_yhtenaista_tunnistaa_uuden_muodon_sarakkeet():
    raaka = pd.DataFrame([
        ['Toimittajan nimi', 'Y-tunnus', 'Summa (alv 0%)', 'Tositepvä', 'Tili- numero', 'Palvelu-luokka', 'Kunnan y-tunnus'],
        ['Firma Oy', '1234567-8', 5, '2025-03-01', '4340', '3051', '0136169-2'],
    ])
    rivi = p.yhtenaista(raaka, 2025).iloc[0]
    assert (rivi.ytunnus, rivi.palveluluokka, rivi.tili) == ('1234567-8', '3051', '4340')


def test_yhtenaista_pysahtyy_jos_pakollinen_sarake_puuttuu():
    with pytest.raises(SystemExit):
        p.yhtenaista(pd.DataFrame([['Toimittaja', 'Summa'], ['Firma', 1]]), 2030)


# ---------- arviointi ----------
def _rivit(*rivit):
    return pd.DataFrame(rivit, columns=['palveluluokka', 'tili', 'ytunnus', 'toimielin', 'summa'])


def test_ennusta_kayttaa_tarkinta_tasmaavaa_avainta():
    opetus = _rivit(('3051', '4340', 'A', 'Koulutus', 100), ('3051', '4340', 'B', 'Tekninen', 900),
                    ('3051', '4500', 'B', 'Tekninen', 50))
    kohde = _rivit(('3051', '4340', 'A', None, 1),      # sama toimittaja → Koulutus, vaikka luokan enemmistö on Tekninen
                   ('3051', '4500', 'C', None, 1),      # sama tili → Tekninen
                   ('9999', '4340', 'A', None, 1))      # tuntematon palveluluokka → ei arviota
    arvio = p.ennusta(opetus, kohde, 'toimielin')
    assert list(arvio[:2]) == ['Koulutus', 'Tekninen'] and pd.isna(arvio[2])


def test_ennusta_ei_arvaa_kynnyksen_alla():
    opetus = _rivit(('5501', '4340', 'A', 'Konserni', 60), ('5501', '4340', 'B', 'Tekninen', 40))
    arvio = p.ennusta(opetus, _rivit(('5501', '4340', 'C', None, 1)), 'toimielin')
    assert pd.isna(arvio[0])                            # 60 % < 80 %


def test_ennusta_painottaa_euroilla_ja_kasittelee_hyvitykset_itseisarvoina():
    opetus = _rivit(('3051', '4340', 'A', 'Koulutus', -900), ('3051', '4340', 'B', 'Tekninen', 100))
    arvio = p.ennusta(opetus, _rivit(('3051', '4340', 'C', None, 1)), 'toimielin')
    assert arvio[0] == 'Koulutus'


def test_arvioi_puuttuvat_oppii_vain_edellisista_vuosista_eika_omista_arvioistaan():
    d = pd.DataFrame({
        'vuosi': [2022, 2023, 2024, 2025, 2025],
        'palveluluokka': ['3051'] * 4 + ['7777'],
        'tili': ['1'] * 5, 'ytunnus': ['A'] * 5, 'summa': [10.0] * 5,
        'toimielin': ['Vanha', 'Uusi', 'Uusi', None, None],
        'tulosalue': ['T'] * 3 + [None, None],
    })
    yhteenveto = p.arvioi_puuttuvat(d)
    assert d.toimielin[3] == 'Uusi' and pd.isna(d.toimielin[4])
    assert list(d.arvio) == [0, 0, 0, 1, 0]
    assert yhteenveto['toimielin'][2025] == {'opetusvuodet': [2023, 2024], 'kattavuus': 0.5}


def test_takautuva_testi_laskee_osuvuuden():
    d = pd.DataFrame({
        'vuosi': [2022, 2023, 2024, 2024],
        'palveluluokka': ['3051', '3051', '3051', '3051'],
        'tili': ['1'] * 4, 'ytunnus': ['A'] * 4, 'summa': [10.0, 10.0, 30.0, 10.0],
        'toimielin': ['K', 'K', 'K', 'Muu'], 'tulosalue': [None] * 4,
    })
    t = p.takautuva_testi(d)['toimielin']
    assert (t['testivuosi'], t['opetusvuodet'], t['kattavuus'], t['osuvuus']) == (2024, [2022, 2023], 1.0, 0.75)


# ---------- toimittajien luokittelu ----------
@pytest.mark.parametrize('nimi, muoto, odotus', [
    ('Liedon kunta', None, 'Julkinen sektori'),
    ('Paimion Latu ry', None, 'Järjestö tai säätiö'),
    ('Rakennus Oy', None, 'Yritys'),
    ('Kuntaliitto Palvelut Oy', 'Osakeyhtiö', 'Yritys'),         # yhtiömuoto voittaa nimen
    ('Matti Meikäläinen', None, 'Ei tiedossa'),
])
def test_paattele_tyyppi(nimi, muoto, odotus):
    assert p.paattele_tyyppi(nimi, muoto) == odotus


def test_paattele_kunta_jarjestys():
    koodit = {'577': 'Paimio'}
    assert p.paattele_kunta('1-1', 'Turun kaupunki', {'kuntakoodi': '577'}, koodit) == 'Paimio'   # PRH ensin
    assert p.paattele_kunta('0828255-9', 'V-S Sairaanhoitopiiri', {}, koodit) == 'Turku'          # käsin asetettu
    assert p.paattele_kunta('', 'Salon Kaupunki', {}, koodit) == 'Salo'                           # nimestä
    assert p.paattele_kunta('', 'Salon Rakennus Oy', {}, koodit) is None                          # yritystä ei arvata


def test_ulkomaiseksi_merkitaan_vain_maakoodin_perusteella():
    d = pd.DataFrame({
        'vuosi': [2021, 2025], 'ytunnus': [None, None], 'toimittaja': ['Vanha Firma', 'Topcart GmbH'],
        'maa': [None, 'DE'], 'summa': [1.0, 2.0],
    })
    t = p.luokittele_toimittajat(d, {}, {}, {})
    assert t.loc['N:Vanha Firma', 'kunta'] == 'Ei tiedossa'      # maakoodi puuttuu → ei oleteta ulkomaiseksi
    assert t.loc['N:Topcart GmbH', 'kunta'] == 'Ulkomaat'


def test_palveluluokan_nimi():
    nimet = {'3051': 'Perusopetus'}
    assert p.palveluluokan_nimi('3051', nimet) == '3051 Perusopetus'
    assert p.palveluluokan_nimi('I3051', nimet) == 'I3051 Perusopetus (I-koodi)'
    assert p.palveluluokan_nimi('PL21', nimet) == 'PL21'


# ---------- PRH-välimuisti ja lähteet ----------
def test_prh_vanhentuneet():
    tanaan = date(2026, 11, 26)
    muisti = {
        'tuore': {'kuntakoodi': '577', 'haettu': '2026-09-23'},
        'vanha': {'kuntakoodi': '577', 'haettu': '2025-01-01'},
        'tyhja_tuore': {'haettu': '2026-10-01'},
        'tyhja_vanha': {'haettu': '2026-06-01'},
        'paivaton': {'kuntakoodi': '577'},
    }
    assert p.prh_vanhentuneet(muisti, list(muisti) + ['uusi'], tanaan) == ['vanha', 'tyhja_vanha', 'uusi']


def test_etsi_uudet_lahteet():
    html = ('<a href="https://www.paimio.fi/uploads/2026/06/aa-ostolaskut_vuodelta_2025.xlsx">2025</a>'
            '<a href="https://www.paimio.fi/uploads/2027/06/bb-ostolaskut-vuodelta-2026.xlsx">2026</a>'
            '<a href="https://www.paimio.fi/uploads/2027/06/tilinpaatos-2026.pdf">muu</a>')
    lahteet = {2025: 'vanha-osoite'}
    assert p.etsi_uudet_lahteet(lahteet, html) == [2026]
    assert lahteet[2025] == 'vanha-osoite' and lahteet[2026].endswith('ostolaskut-vuodelta-2026.xlsx')


# ---------- versio ----------
def test_versio_on_muutoslokin_uusin():
    loki = (p.ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    assert re.search(r'^## (\d+\.\d+\.\d+)$', loki, re.M).group(1) == p.VERSIO


def test_sivulla_on_sama_versio():
    sivu = p.ROOT / 'index.html'
    if not sivu.exists():
        pytest.skip('index.html puuttuu')
    assert f'>Versio {p.VERSIO}<' in sivu.read_text(encoding='utf-8')


# ---------- valmis sivu vastaa lähdetiedostoja ----------
def _sivun_data():
    sivu = p.ROOT / 'index.html'
    if not sivu.exists():
        pytest.skip('index.html puuttuu')
    m = re.search(r'const DATA = (\{.*?\});\n', sivu.read_text(encoding='utf-8'))
    return json.loads(m.group(1).replace('<\\/', '</'))


def test_sivun_vuosisummat_vastaavat_exceleita():
    data = _sivun_data()
    for i, vuosi in enumerate(data['years']):
        tiedosto = p.LAHDE / f'ostolaskut_{vuosi}.xlsx'
        if not tiedosto.exists():
            pytest.skip('lähdetiedostot puuttuvat')
        raaka = pd.read_excel(tiedosto, header=None)
        sarake = next(c for c in raaka.columns if raaka[c].map(lambda v: p.SARAKKEET.get(p.normalisoi(v)) == 'summa').any())
        excel = pd.to_numeric(raaka[sarake], errors='coerce').sum()
        sivu = sum(r[6] for r in data['rows'] if r[0] == i) / 100
        assert sivu == pytest.approx(excel, abs=0.01), vuosi


def test_sivun_data_on_ehja():
    data = _sivun_data()
    assert all(len(r) == len(p.RIVI) for r in data['rows'])
    for sarake, dim in ((2, None), (3, 'tilil'), (4, 'toimielin'), (5, 'tulosalue'), (9, 'palveluluokka')):
        koko = len(data['sup']) if dim is None else len(data['dims'][dim])
        assert all(0 <= r[sarake] < koko for r in data['rows'])
    # arvioituja rivejä saa olla vain vuosilla, joilta kaupungin tieto puuttuu
    arvioidut = {data['years'][r[0]] for r in data['rows'] if r[8]}
    assert arvioidut == {int(v) for a in data['arviot'].values() for v in a}
