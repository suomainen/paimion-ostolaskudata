# Työkalut: sivun päivitys

Näillä tiedostoilla kootaan repon juuren `index.html` uudelleen, kun kaupunki julkaisee uutta ostolaskudataa.

## Kansiorakenne

```
paimion-ostolaskudata/        (GitHub-repo)
├── index.html                valmis sivu (koottu tiedosto, älä muokkaa käsin)
├── README.md
├── requirements.txt          Python-kirjastot
├── .gitignore                jättää lahdedata-kansion pois GitHubista
├── lahdedata/                kaupungin Excel-tiedostot (vain omalla koneella)
└── tyokalut/
    ├── paivita.py            koko päivitys yhdellä ajolla
    ├── test_paivita.py       testit
    ├── template.html         sivun pohja (HTML, CSS, JavaScript)
    ├── lahteet.json          vuosien Excel-tiedostojen osoitteet paimio.fi:ssä
    ├── prh_valimuisti.json   PRH:sta haetut toimittajatiedot ja hakupäivät
    ├── palveluluokat.json    palveluluokkien nimet (Valtiokonttorin koodisto)
    ├── tunnistamattomat.csv  toimittajat, joiden kunta tai tyyppi jäi tunnistamatta (skripti kirjoittaa)
    ├── tee_kartta.py         tekee tiedoston kartta.json Tilastokeskuksen rajapinnasta
    ├── kartta.json           kunta- ja maakuntarajat SVG-polkuina (Tilastokeskus 2025, 1:4,5 milj., CC BY 4.0)
    ├── tee_kuva.py           tekee otsikkokuvan hero.svg
    ├── hero.svg              otsikkokuva (koodilla tehty, MIT)
    └── rubik-latin.woff2     Rubik-fontti (SIL OFL 1.1)
```

Kaupungin Excel-tiedostot ovat kansiossa `lahdedata`, joko repon juuressa tai sen vieressä. Jos kansiota ei ole, skripti luo sen repon juureen ja lataa tiedostot. Kansio ei mene GitHubiin.

## Päivitys

1. Asenna kirjastot kerran:
   ```
   pip install -r requirements.txt
   ```
2. Aja skripti repon juuressa:
   ```
   python tyokalut/paivita.py
   ```
   Skripti tekee seuraavat asiat ja tulostaa jokaisesta rivin:
   - tarkistaa kaupungin Talous-sivulta, onko siellä uusia vuosia, ja lisää ne tiedostoon `lahteet.json`
   - lataa puuttuvat Excelit ja tulostaa rivimäärät ja summat vuosittain
   - ajaa takautuvan testin arviointimenetelmälle ja arvioi puuttuvat toimielimet ja tulosalueet
   - hakee PRH:sta uudet toimittajat sekä ne, joiden tiedot ovat yli vuoden vanhoja
   - kirjoittaa tiedoston `tunnistamattomat.csv`
   - kokoaa `index.html`:n
3. Aja testit. Ne tarkistavat muun muassa, että sivun vuosisummat vastaavat Exceleitä sentilleen:
   ```
   pip install pytest
   python -m pytest tyokalut
   ```
4. Avaa `index.html` selaimessa ja katso, että uusi vuosi näyttää järkevältä.
5. Käy `tunnistamattomat.csv`:n alku läpi. Jos listan kärjessä on uusi iso toimittaja, lisää sen kotikunta `paivita.py`:n `KUNTA_KASIN`-sanakirjaan.
6. Lataa GitHubiin `index.html` ja muuttuneet `tyokalut`-tiedostot. Päivitä `README.md`:n vuositaulukko ja testitulokset.

Jos kaupunki julkaisee tiedoston nimellä, jota skripti ei tunnista, lisää osoite käsin tiedostoon `lahteet.json`:

```json
"2026": "https://www.paimio.fi/uploads/2027/06/xxxxxxxx-ostolaskut_vuodelta_2026.xlsx"
```

## Jos jokin menee pieleen

- **"Sarakkeita ei tunnistettu":** kaupunki on muuttanut sarakkeiden nimiä. Lisää uusi nimi `paivita.py`:n `SARAKKEET`-sanakirjaan pienillä kirjaimilla ja ilman välilyöntejä, viivoja ja pisteitä. Esimerkiksi sarake "Summa €" lisätään muodossa `'summa€': 'summa'`.
- **Takautuvan testin osuvuus putoaa:** kaupungin organisaatio tai kirjauskäytäntö on todennäköisesti muuttunut. Arvioihin ei silloin kannata luottaa. Kynnystä voi nostaa vakiolla `ARVIO_KYNNYS`, jolloin arvioita tehdään vähemmän mutta varmemmin.
- **Kuntajako muuttuu:** aja `python tyokalut/tee_kartta.py 2026` ja vaihda `paivita.py`:n `LUOKITUS`-vakion arvoksi `'20260101'`.
- **Toimittajan kunta näkyy "Ei tiedossa":** PRH:n avoimessa rajapinnassa ei ole kuntia, kuntayhtymiä, yhdistyksiä eikä säätiöitä. Lisää Y-tunnus ja kunta `KUNTA_KASIN`-sanakirjaan tai kunnan genetiivimuoto `KUNTA_GENETIIVI`-sanakirjaan.
- **Toimittajatiedot halutaan hakea heti uudelleen:** poista `prh_valimuisti.json`. Haku kestää muutaman minuutin. Muuten tiedot päivittyvät itsestään vuoden välein, ja rajapinnasta puuttuvia yritetään uudelleen 90 päivän välein.

## Sivun muokkaaminen

Ulkoasu ja toiminnot ovat tiedostossa `template.html`. Paikkamerkit `__DATA__`, `__MAP__`, `__FONT__`, `__HERO__`, `__DOWNLOADS__` ja `__YEARS__` korvataan ajon aikana. Skripti pysähtyy, jos jokin niistä puuttuu.

Datan rivit ovat taulukoita, joiden sarakkeet on nimetty kahdessa paikassa: `paivita.py`:n `RIVI` ja `template.html`:n `const C`. Jos lisäät sarakkeen, lisää se molempiin.

Otsikkokuvan värejä ja kuviota muutetaan tiedostossa `tee_kuva.py`. Aja se ja sen jälkeen `paivita.py`.
