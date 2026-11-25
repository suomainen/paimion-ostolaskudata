# Paimion kaupungin ostolaskudata

Selattava verkkosivu Paimion kaupungin julkaisemasta ostolaskudatasta vuosilta 2020–2025. Sivulla voi tarkastella kaupungin ostoja vuosittain, toimittajittain, tileittäin, toimielimittäin ja toimittajan sijainnin tai toimialan mukaan.

Sivusto: **https://suomainen.github.io/paimion-ostolaskudata/**

> **Huom.** Tämä on epävirallinen katselusivu kaupungin avoimesta datasta. Se ei ole Paimion kaupungin ylläpitämä palvelu. Virallinen aineisto löytyy kaupungin [Talous-sivulta](https://www.paimio.fi/kaupunki-ja-hallinto/talous/).
>
> Sivu ja sen koodi on tehty tekoälyavustajan avulla, ja tiedoissa voi olla virheitä. Tarkista olennaiset tiedot kaupungin alkuperäisestä aineistosta. Korjaukset ja huomiot: oskari@summanen.org tai [GitHubin issues](https://github.com/suomainen/paimion-ostolaskudata/issues).

## Tausta

Sivun lähtökohtana on valtuustoaloite *Paimion kaupungin ostolaskudatan selainpohjainen ja ajantasainen julkaiseminen verkkosivuilla*. Aloitteen jätti Oskari Summanen valtuustoryhmien puolesta (SDP, PS, KD, Vihr. ja Vas.) kaupunginvaltuuston kokouksessa 22.4.2026 (§ 19).

Aloitteessa esitetään, että Paimio siirtyy Excel-tiedostoina julkaistavasta ostolaskudatasta selainpohjaiseen raportointiin, jossa edellisen kuukauden ostolaskudata on nähtävillä kaupungin verkkosivuilla. Aloitteessa ehdotetaan lisäksi teknistä toteutusta, jota voi käyttää ilman erillisiä ohjelmia tai latauksia, ja toteutuksen aloittamista vuoden 2026 loppuun mennessä.

Tämä sivu on aloitteen tekijän tekemä esimerkkitoteutus. Se näyttää, miltä selainpohjainen raportointi voisi näyttää kaupungin jo julkaisemalla datalla.

- [Kokousasia: Kaupunginvaltuusto 22.4.2026 § 19](https://julkaisu.paimio.fi/dynasty10/cgi/DREQUEST.PHP?page=meetingitem&id=2026733-12)
- [Aloite (PDF)](https://julkaisu.paimio.fi/dynasty10/kokous/2026733-12-39533.PDF)

## Ominaisuudet

- Vuosivalinta 2020–2025 ja vuosien välinen vertailu
- Tunnusluvut: ostot yhteensä, toimittajien ja tositteiden määrä, keskimääräinen rivi, paikallisten ja maakunnallisten toimittajien osuus
- Ostot kuukausittain tositepäivämäärän mukaan. Kuukauden voi valita kaaviosta tai pudotusvalikosta, jolloin koko raportti rajautuu siihen.
- Toimittajalista hakutoiminnolla. Toimittajaa napsauttamalla näkyvät sen ostot vuosittain, tileittäin ja laskuriveittäin.
- Kuntakartta, jossa kunnat on väritetty toimittajien ostosumman tai toimittajamäärän mukaan. Kartan voi rajata koko Suomeen tai Varsinais-Suomeen, ja kuntaa napsauttamalla raportti rajautuu siihen.
- Jakaumat maakunnittain, kunnittain, toimialoittain ja toimittajan tyypin mukaan (yritys, julkinen sektori, järjestö tai säätiö)
- Rajaukset toimielimen, tilin, tulosalueen, palveluluokan, kunnan, maakunnan ja toimialan mukaan. Rajaukset voi yhdistää.
- Pysyvät linkit: näkymän tila (vuosi, rajaukset, välilehti, avattu toimittaja) on sivun osoitteessa nimillä ja koodeilla, joten linkki vie samaan näkymään myös aineiston päivityksen jälkeen. Linkin saa painikkeesta Kopioi linkki näkymään.
- Analyysit-välilehti: ostojen kehitys vuosittain valitulla jaottelulla (esimerkiksi toimiala tai tili), uudet ja poistuneet toimittajat, paikallisuus tileittäin, toimittajat ostojen koon mukaan sekä paikallisuus ja keskittyneisyys vuosittain
- Palveluluokat: mihin kaupungin palveluun ostot kohdistuvat (Valtiokonttorin kuntien yhteinen luokitus, aineistossa vuodesta 2022)
- Toimii puhelimella, tabletilla ja tietokoneella sekä näppäimistöllä ja ruudunlukijalla (WCAG 2.1 AA)

## Käyttö

Sivu on yksi itsenäinen `index.html`-tiedosto, johon data on upotettu. Palvelinta tai asennuksia ei tarvita.

- **Paikallisesti:** avaa `index.html` selaimessa.
- **GitHub Pagesissa:** Settings → Pages → Source: *Deploy from a branch*, haara `main`, kansio `/ (root)`.

Sivu ei hae mitään verkosta. Data, kuntakartta, Rubik-fontti ja otsikkokuva on upotettu tiedostoon, joten sivu toimii myös ilman verkkoyhteyttä. Rubik-fontti on julkaistu [SIL Open Font License 1.1](https://openfontlicense.org) -lisenssillä.

## Aineisto

### Ostolaskudata

Lähde: [Paimion kaupunki, ostolaskut 2020–2025](https://www.paimio.fi/kaupunki-ja-hallinto/talous/)

Kaupungin kuvaus aineistosta:

> Aineisto sisältää Paimion kaupungin palvelujen, aineiden, tarvikkeiden ja tavaroiden ostot sekä kuntien kirjanpidossa tiliryhmiin vuokrakulut ja muut toimintakulut kuuluvat ostot tiliöintirivitasolla. Summat ovat arvonlisäverottomia, loppukustannuksia kaupungille. Aineistosta on poistettu yksityishenkilöille maksetut laskut.
>
> Aineiston julkaisemisessa on noudatettu Kuntaliiton julkaisemaa Kuntien ja kuntayhtymien ostolaskudatan avaamisen ohjetta. Tiedot on poimittu kaupungin kirjanpitojärjestelmästä ja aineistoa on täydennetty YTJ:stä suomalaisten yritysten tiedoilla.
>
> Tiedot päivitetään vuosittain tilinpäätöksen hyväksymisen jälkeen.

Vuosittaiset Excel-tiedostot yhdistettiin yhdeksi aineistoksi. Sarakkeiden nimet ja järjestys vaihtelevat vuosittain, joten ne yhtenäistettiin. Lisäksi toimielinten nimien lyhenteet yhtenäistettiin, esimerkiksi "Tekninen ltk" muutettiin muotoon "Tekninen lautakunta". Rivien summia ei ole muutettu.

| Vuosi | Rivejä | Ostot (alv 0 %) |
|------:|-------:|----------------:|
| 2020 | 15 331 | 42 147 443 € |
| 2021 | 16 528 | 46 682 619 € |
| 2022 | 13 268 | 47 077 910 € |
| 2023 | 11 613 | 16 887 774 € |
| 2024 | 11 611 | 25 297 654 € |
| 2025 | 11 989 | 20 936 543 € |

### Toimittajatietojen rikastus

Toimittajien kunta, maakunta, päätoimiala ja yhtiömuoto haettiin Y-tunnuksella [PRH:n avoimesta YTJ-rajapinnasta](https://avoindata.prh.fi/). Kartan kunta- ja maakuntarajat ovat Tilastokeskuksen avoimesta aineistosta (kunnat ja maakunnat 2025, 1:4 500 000, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.fi)). Kuntakoodit muutettiin kuntien ja maakuntien nimiksi [Tilastokeskuksen luokitusten](https://www.stat.fi/fi/luokitukset) avulla (kunnat ja maakunnat 2025).

## Rajoitukset ja huomiot

- **Sote-siirto 2023:** Vuodesta 2023 alkaen sosiaali- ja terveyspalvelut sekä pelastustoimi siirtyivät Varsinais-Suomen hyvinvointialueelle. Siksi ostot laskevat selvästi vuodesta 2022 vuoteen 2023.
- **Vuosi 2025:** Aineistossa ei ole toimielin- eikä tulosaluetietoa. Ne on arvioitu palveluluokan, tilin ja toimittajan perusteella vuosien 2023–2024 aineistosta. Arvio tehdään vain, kun vähintään 80 % aiempien vuosien euroista on kuulunut samaan luokkaan; muut rivit jäävät ilman tietoa. Toimielin saatiin arvioitua 90 %:lle ja tulosalue 87 %:lle vuoden 2025 euroista. Arvioidut rivit on merkitty sivulla.
- **Arvion luotettavuus:** `paivita.py` testaa menetelmän jokaisella ajolla arvioimalla samalla tavalla vuoden 2024, jonka oikeat tiedot tunnetaan, vuosien 2022–2023 perusteella. Viimeisimmässä ajossa toimielin osui oikein 99,2 %:ssa arvioiduista euroista (arvio kattoi 90,8 % euroista) ja tulosalue 96,3 %:ssa (kattavuus 96,2 %). Luvut näkyvät myös sivun huomioissa.
- **Tositepäivämäärät:** Vuoden aineistoon kuuluu myös edellisen ja seuraavan vuoden päivämäärällä olevia tositteita, koska aineisto on rajattu tilikauden mukaan.
- **YTJ-tiedot kuvaavat nykytilaa**, eivät laskun aikaista tilannetta. Esimerkiksi toimittajan kotikunta tai toimiala on voinut muuttua. Tiedot haetaan uudelleen vuoden välein.
- **Kotikunta on yrityksen rekisteröity osoite**, ei välttämättä paikka, jossa palvelu tuotetaan. Valtakunnalliset yritykset näkyvät usein pääkonttorinsa kunnassa, mikä kasvattaa esimerkiksi Helsingin ja Uudenmaan osuutta.
- **Puuttuvat YTJ-tiedot:** PRH:n avoimessa rajapinnassa ei ole kuntia, kuntayhtymiä, yhdistyksiä, säätiöitä eikä osaa toiminimistä. Niiden osuus ostojen euroista on noin 45 %. Näiden toimittajien tyyppi ja kunta on päätelty nimestä, esimerkiksi "Liedon kunta" → Lieto. Muutaman kuntayhtymän kotikunta on asetettu käsin. Loput on merkitty "Ei tiedossa".
- **Hyvityslaskut** näkyvät negatiivisina riveinä ja vähentävät summia. Hyvitysten määrä näkyy Ostot yhteensä -luvun alla. Jos jonkin ryhmän summa on negatiivinen, sille ei näytetä palkkia eikä prosenttiosuutta.
- **Palveluluokan I-alkuiset koodit** (esimerkiksi I3051) eivät kuulu viralliseen luokitukseen. Ne ovat kaupungin omia, todennäköisesti investointeja samalle palvelulle.

## Päivittäminen

Sivu kootaan kansion `tyokalut` skriptillä: `python tyokalut/paivita.py`. Skripti tarkistaa kaupungin Talous-sivulta uudet vuodet, lataa aineistot, ajaa arvioinnin takautuvan testin ja kokoaa `index.html`:n. Testit ajetaan komennolla `python -m pytest tyokalut`. Tarkemmat ohjeet ovat tiedostossa [tyokalut/LUEMINUT.md](tyokalut/LUEMINUT.md).

## Saavutettavuus

Sivu noudattaa WCAG 2.1 AA -tasoa. Ratkaisut ovat pohjassa `tyokalut/template.html`:

- ohituslinkki sisältöön, otsikkotasot ilman hyppyjä ja maamerkit (navigaatio, sisältö, alatunniste)
- kaikki toiminnot näppäimistöllä: vuodet, kaavioiden pylväät, palkkiluettelot, taulukoiden lajittelu ja rivien valinta. Kohdistus säilyy samassa kohdassa, kun näkymä päivittyy.
- toimittajan tiedot avautuvat modaalisena ikkunana: kohdistus siirtyy ikkunaan, tausta ei ole käytettävissä, ja Esc palauttaa kohdistuksen avanneeseen riviin
- kartta on kuva, jolla on tekstivaihtoehto: Kunta-valikko ja Toimittajat kunnittain -luettelo tekevät saman kuin kartan napsauttaminen
- ruudunlukijalle tilaviesti, kun rajaus muuttaa näkymää, ja maininta uuteen välilehteen avautuvista linkeistä
- tekstin kontrasti vähintään 4,5:1, näkyvä kohdistuskehys, ei vaakavieritystä 320 px leveydellä, liike pois käyttöjärjestelmän asetuksen mukaan

Pohjan muutosten jälkeen tarkistetaan vähintään:

- automaattinen tarkistus (axe) yhteenvedossa, rajatussa näkymässä, analyyseissä ja toimittajan ikkunassa 1280 px ja 375 px leveydellä
- käyttö pelkällä näppäimistöllä: ohituslinkki, välilehdet nuolinäppäimillä, rajaus taulukosta, toimittajan ikkunan avaus ja sulku
- 320 px leveä näkymä ilman vaakavieritystä

Nämä ajaa `tyokalut/tarkista_sivu.js`, joka tarkistaa lisäksi linkkien pysyvyyden ja analyysien luvut:

```
npm install --no-save playwright axe-core
npx playwright install chromium
node tyokalut/tarkista_sivu.js
```

Tiedossa olevat rajoitukset: sivua ei ole testattu oikeilla ruudunlukijoilla (NVDA, VoiceOver), vaan automaattisella tarkistuksella ja näppäimistöllä. Kartan värisävyjen erot eivät yksinään välitä lukuja, joten tarkat arvot ovat luettelossa. Linkitetyt Excel-tiedostot ovat kaupungin julkaisemia, eikä niiden saavutettavuus ole tämän sivun hallinnassa.

## Versiointi

Versionumero on muotoa pää.osa.korjaus, ja muutokset kirjataan tiedostoon [CHANGELOG.md](CHANGELOG.md). Kun sivu muuttuu:

1. nosta `tyokalut/paivita.py`:n `VERSIO` ja lisää kohta tiedoston `CHANGELOG.md` alkuun (testi tarkistaa, että ne täsmäävät)
2. aja `python tyokalut/paivita.py`, `python -m pytest tyokalut` ja `node tyokalut/tarkista_sivu.js`
3. `git commit`, `git tag -a vX.Y.Z -m "Kuvaus"` ja `git push --follow-tags`

Pelkkä dokumentaation tai työkalujen muutos ei nosta numeroa.

## Miten sivu on tehty

Sivu on tehty yhdessä Clauden kanssa, Anthropicin tekoälyavustajalla, jota käytettiin Claude-sovelluksen Cowork-tilassa. Koko työ tehtiin parin kahvimukillisen aikana.

## Lisätietoa

- [Kuntien ja kuntayhtymien ostolaskudatan avaamisen ohje](https://www.kuntaliitto.fi/julkaisut/2021/2112-kuntien-ja-kuntayhtymien-ostolaskudatan-avaamisen-ohje) (Kuntaliitto 2021)
- [Kuntien ja kuntayhtymien ostolaskut](https://www.kuntaliitto.fi/talous/kirjanpito-ja-tilinpaatos/kuntien-ja-kuntayhtymien-ostolaskut) (Kuntaliitto)
- [Kuntien ostolaskujen ja muiden asiakirjojen julkisuus](https://www.kuntaliitto.fi/laki/julkisuus-ja-tietosuoja/kunnille-saapuvat-tietopyynnot/kuntien-ostolaskujen-ja-muiden-asiakirjojen-julkisuus) (Kuntaliitto)

## Lisenssi

Sivun koodi on julkaistu MIT-lisenssillä (katso `LICENSE`).

Lisenssi ei koske aineistoja. Ostolaskudata on Paimion kaupungin julkaisemaa avointa dataa, toimittajatiedot ovat PRH:n avointa dataa ja kuntarajat Tilastokeskuksen avointa dataa (CC BY 4.0). Niihin sovelletaan kunkin julkaisijan käyttöehtoja. Otsikkokuva on tehty tämän repon koodilla (`tyokalut/tee_kuva.py`) ja kuuluu MIT-lisenssin piiriin.
