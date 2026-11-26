# Työkalut: sivun päivitys

Näillä tiedostoilla kootaan repon juuren `index.html` uudelleen, kun kaupunki julkaisee uutta ostolaskudataa.

## Kansiorakenne

```
paimion-ostolaskudata/        (GitHub-repo)
├── index.html                valmis sivu (koottu tiedosto, älä muokkaa käsin)
├── README.md
├── CHANGELOG.md              muutosloki, uusin versio ensin
├── requirements.txt          Python-kirjastot
├── .gitignore                jättää lahdedata-kansion pois GitHubista
├── lahdedata/                kaupungin Excel-tiedostot (vain omalla koneella)
└── tyokalut/
    ├── paivita.py            koko päivitys yhdellä ajolla
    ├── test_paivita.py       testit datan käsittelylle (pytest)
    ├── tarkista_sivu.js      selaintarkistus valmiille sivulle (Playwright ja axe)
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
   Jos muutit pohjaa `template.html`, aja myös selaintarkistus (vaatii Node.js:n, asennusohje tiedoston alussa):
   ```
   node tyokalut/tarkista_sivu.js
   ```
4. Avaa `index.html` selaimessa ja katso, että uusi vuosi näyttää järkevältä.
5. Käy `tunnistamattomat.csv`:n alku läpi. Jos listan kärjessä on uusi iso toimittaja, lisää sen kotikunta `paivita.py`:n `KUNTA_KASIN`-sanakirjaan.
6. Nosta `paivita.py`:n `VERSIO`, lisää kohta tiedostoon `CHANGELOG.md` ja aja skripti uudelleen, jotta numero päivittyy sivulle. Päivitä `README.md`:n vuositaulukko ja testitulokset.
7. Vie GitHubiin: `git add -A`, `git commit`, `git tag -a vX.Y.Z -m "Kuvaus"` ja `git push --follow-tags`.

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

Ulkoasu ja toiminnot ovat tiedostossa `template.html`. Paikkamerkit `__DATA__`, `__MAP__`, `__FONT__`, `__HERO__`, `__DOWNLOADS__`, `__YEARS__` ja `__VERSION__` korvataan ajon aikana. Skripti pysähtyy, jos jokin niistä puuttuu.

Tekstit ja kielet: suomenkieliset kiinteät tekstit ovat HTML:ssä, ja jokaisella käännettävällä elementillä on avain (`data-t="avain"`, attribuuteille `data-ta="aria-label:avain"`). Ruotsin ja englannin tekstit ovat samoilla avaimilla skriptin taulukossa `T`, jossa ovat myös koodissa muodostettavat tekstit kaikilla kolmella kielellä (funktio `t`). Kun lisäät tekstin, lisää avain kaikkiin kieliin; `tarkista_sivu.js` ilmoittaa puuttuvasta käännöksestä. Aineiston arvoja ei käännetä, paitsi taulukon `ARVOT` yleiset luokat, maakunnat ja kuntien ruotsinkieliset nimet.

Värit ovat CSS-muuttujina kohdassa `:root`, ja tumma ulkoasu määrittelee ne uudelleen kohdassa `:root[data-teema="tumma"]`. Käytä uusissa tyyleissä muuttujia, älä kiinteitä värejä.

Näkymän tila tallennetaan osoitteeseen funktioissa `lueOsoite` ja `saveHash`. Jos lisäät rajauksen tai valinnan, lisää se molempiin ja tarkistukseen `tarkista_sivu.js`, jotta vanhat linkit pysyvät toimivina.

Datan rivit ovat taulukoita, joiden sarakkeet on nimetty kahdessa paikassa: `paivita.py`:n `RIVI` ja `template.html`:n `const C`. Toimittajan sarakkeet ovat vastaavasti `kokoa_data`-funktion `sup`-listassa ja vakiossa `const P`. Jos lisäät sarakkeen, lisää se molempiin.

Otsikkokuvan värejä ja kuviota muutetaan tiedostossa `tee_kuva.py`. Aja se ja sen jälkeen `paivita.py`.

Saavutettavuuden tarkistuslista on `README.md`:n kohdassa Saavutettavuus. Käy se läpi aina, kun muutat pohjaa.
