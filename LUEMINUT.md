# Työkalut: sivun päivitys

Näillä tiedostoilla kootaan repon juuren `index.html` uudelleen, kun kaupunki julkaisee uuden vuoden ostolaskudatan.

## Kansiorakenne

```
paimion-ostolaskudata/        (GitHub-repo = paikallinen kansio "sivusto")
├── index.html                valmis sivu
├── README.md
├── .gitignore                jättää lahdedata-kansion pois GitHubista
└── tyokalut/
    ├── paivita.py            koko päivitys yhdellä ajolla
    ├── lahteet.json          vuosien Excel-tiedostojen osoitteet paimio.fi:ssä
    ├── template.html         sivun pohja (HTML, CSS, JavaScript)
    ├── kartta.json           kunta- ja maakuntarajat SVG-muodossa (Tilastokeskus 2025, 1:4,5 milj.)
    ├── prh_valimuisti.json   PRH:sta jo haetut toimittajatiedot
    ├── rubik-latin.woff2     Rubik-fontti (SIL OFL 1.1)
    └── hero.jpg              otsikkokuva (Paimion kaupunki, paimio.fi)
```

Skripti etsii kaupungin Excel-tiedostot kansiosta `lahdedata`, joko repon juuresta tai sen vierestä. Jos kansiota ei löydy, skripti luo sen repon juureen ja lataa tiedostot `lahteet.json`:n osoitteista. Kansio ei mene GitHubiin, koska se on lueteltu `.gitignore`-tiedostossa.

## Uuden vuoden lisääminen

1. Etsi uuden vuoden Excel-tiedoston osoite kaupungin [Talous-sivulta](https://www.paimio.fi/kaupunki-ja-hallinto/talous/). Löydät sen hiiren oikealla painikkeella → Kopioi linkin osoite.
2. Lisää osoite tiedostoon `lahteet.json`, esimerkiksi:
   ```json
   "2026": "https://www.paimio.fi/uploads/2027/06/xxxxxxxx-ostolaskut_vuodelta_2026.xlsx"
   ```
3. Asenna tarvittavat kirjastot, jos niitä ei vielä ole:
   ```
   pip install pandas openpyxl pillow
   ```
4. Aja skripti tässä kansiossa:
   ```
   python paivita.py
   ```
   Skripti lataa puuttuvat Excelit kansioon `lahdedata`, hakee PRH:sta vain uudet toimittajat, kokoaa `index.html`:n repon juureen ja tulostaa lopuksi rivimäärät ja summat vuosittain.
5. Tarkista sivu selaimessa ja vertaa uuden vuoden summaa Excel-tiedostoon.
6. Lataa `index.html` ja muuttuneet `tyokalut`-tiedostot (`lahteet.json`, `prh_valimuisti.json`) GitHubiin ja päivitä tarvittaessa `README.md`:n vuositaulukko.

## Jos jokin menee pieleen

- **"Sarakkeita ei tunnistettu":** kaupunki on muuttanut sarakkeiden nimiä. Lisää uusi nimi `paivita.py`:n `MAP`-sanakirjaan pienillä kirjaimilla ja ilman välilyöntejä, viivoja ja pisteitä. Esimerkiksi sarake "Summa €" lisätään muodossa `'summa€':'summa'`.
- **Kuntien ja maakuntien nimet:** skripti käyttää Tilastokeskuksen vuoden 2025 luokitusta. Kuntaliitosten jälkeen vaihda `LUOKITUS`-muuttujan arvoksi uudempi, esimerkiksi `'20260101'`.
- **Toimittajan kunta näkyy "Ei tiedossa":** PRH:n avoimessa rajapinnassa ei ole kuntia, kuntayhtymiä, yhdistyksiä eikä säätiöitä. Lisää Y-tunnus ja kunta `MANUAL`-sanakirjaan tai kunnan genetiivimuoto `GEN`-sanakirjaan.
- **Vanhentuneet toimittajatiedot:** jos haluat hakea kaikkien toimittajien tiedot PRH:sta uudelleen, poista `prh_valimuisti.json`. Haku kestää muutaman minuutin.

## Sivun muokkaaminen

Ulkoasu ja toiminnot ovat tiedostossa `template.html`. Paikkamerkit `__DATA__`, `__MAP__`, `__FONT__`, `__HERO__`, `__DOWNLOADS__` ja `__YEARS__` korvataan ajon aikana. Älä poista niitä.

Otsikkokuvan voi vaihtaa korvaamalla tiedoston `hero.jpg`. Kuvan kohdistusta säädetään `template.html`:n kohdassa `center 72%`.
