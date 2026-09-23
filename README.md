# Paimion kaupungin ostolaskudata

Selattava verkkosivu Paimion kaupungin julkaisemasta ostolaskudatasta vuosilta 2020–2025. Sivulla voi tarkastella kaupungin ostoja vuosittain, toimittajittain, tileittäin, toimielimittäin ja toimittajan sijainnin tai toimialan mukaan.

> **Huom.** Tämä on epävirallinen katselusivu kaupungin avoimesta datasta. Se ei ole Paimion kaupungin ylläpitämä palvelu. Virallinen aineisto löytyy kaupungin [Talous-sivulta](https://www.paimio.fi/kaupunki-ja-hallinto/talous/).

## Ominaisuudet

- Vuosivalinta 2020–2025 ja vuosien välinen vertailu
- Tunnusluvut: ostot yhteensä, toimittajien ja tositteiden määrä, keskimääräinen rivi, paikallisten ja maakunnallisten toimittajien osuus
- Ostot kuukausittain tositepäivämäärän mukaan. Kuukauden voi valita kaaviosta tai pudotusvalikosta, jolloin koko raportti rajautuu siihen.
- Toimittajalista hakutoiminnolla. Toimittajaa napsauttamalla näkyvät sen ostot vuosittain, tileittäin ja laskuriveittäin.
- Jakaumat maakunnittain, kunnittain, toimialoittain ja toimittajan tyypin mukaan (yritys, julkinen sektori, järjestö tai säätiö)
- Rajaukset toimielimen, tilin, tulosalueen, kunnan, maakunnan ja toimialan mukaan. Rajaukset voi yhdistää, ja ne tallentuvat osoiteriville, joten näkymän voi jakaa linkkinä.
- Toimii puhelimella, tabletilla ja tietokoneella

## Käyttö

Sivu on yksi itsenäinen `index.html`-tiedosto, johon data on upotettu. Palvelinta tai asennuksia ei tarvita.

- **Paikallisesti:** avaa `index.html` selaimessa.
- **GitHub Pagesissa:** Settings → Pages → Source: *Deploy from a branch*, haara `main`, kansio `/ (root)`.

Sivu ei hae mitään verkosta. Data, Rubik-fontti ja otsikkokuva on upotettu tiedostoon (base64), joten sivu toimii myös ilman verkkoyhteyttä. Rubik-fontti on julkaistu [SIL Open Font License 1.1](https://openfontlicense.org) -lisenssillä.

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

Toimittajien kunta, maakunta, päätoimiala ja yhtiömuoto haettiin Y-tunnuksella [PRH:n avoimesta YTJ-rajapinnasta](https://avoindata.prh.fi/). Kuntakoodit muutettiin kuntien ja maakuntien nimiksi [Tilastokeskuksen luokitusten](https://www.stat.fi/fi/luokitukset) avulla (kunnat ja maakunnat 2025).

## Rajoitukset ja huomiot

- **Sote-siirto 2023:** Vuodesta 2023 alkaen sosiaali- ja terveyspalvelut sekä pelastustoimi siirtyivät Varsinais-Suomen hyvinvointialueelle. Siksi ostot laskevat selvästi vuodesta 2022 vuoteen 2023.
- **Vuosi 2025:** Aineistossa ei ole toimielin- eikä tulosaluetietoa. Näiden rajaukset koskevat vain vuosia 2020–2024.
- **Tositepäivämäärät:** Vuoden aineistoon kuuluu myös edellisen ja seuraavan vuoden päivämäärällä olevia tositteita, koska aineisto on rajattu tilikauden mukaan.
- **YTJ-tiedot kuvaavat nykytilaa**, eivät laskun aikaista tilannetta. Esimerkiksi toimittajan kotikunta tai toimiala on voinut muuttua.
- **Puuttuvat YTJ-tiedot:** PRH:n avoimessa rajapinnassa ei ole kuntia, kuntayhtymiä, yhdistyksiä, säätiöitä eikä osaa toiminimistä. Niiden osuus ostojen euroista on noin 45 %. Näiden toimittajien tyyppi ja kunta on päätelty nimestä, esimerkiksi "Liedon kunta" → Lieto. Muutaman kuntayhtymän kotikunta on asetettu käsin. Loput on merkitty "Ei tiedossa".
- **Hyvityslaskut** näkyvät negatiivisina riveinä ja vähentävät summia.

## Miten sivu on tehty

Sivu on tehty yhdessä Clauden kanssa, Anthropicin tekoälyavustajalla, jota käytettiin Claude-sovelluksen Cowork-tilassa. Koko työ tehtiin yhden kahvimukillisen aikana.

## Lisätietoa

- [Kuntien ja kuntayhtymien ostolaskudatan avaamisen ohje](https://www.kuntaliitto.fi/julkaisut/2021/2112-kuntien-ja-kuntayhtymien-ostolaskudatan-avaamisen-ohje) (Kuntaliitto 2021)
- [Kuntien ja kuntayhtymien ostolaskut](https://www.kuntaliitto.fi/talous/kirjanpito-ja-tilinpaatos/kuntien-ja-kuntayhtymien-ostolaskut) (Kuntaliitto)
- [Kuntien ostolaskujen ja muiden asiakirjojen julkisuus](https://www.kuntaliitto.fi/laki/julkisuus-ja-tietosuoja/kunnille-saapuvat-tietopyynnot/kuntien-ostolaskujen-ja-muiden-asiakirjojen-julkisuus) (Kuntaliitto)

## Lisenssi

Sivun koodi on julkaistu MIT-lisenssillä (katso `LICENSE`).

Lisenssi ei koske aineistoja. Ostolaskudata on Paimion kaupungin julkaisemaa avointa dataa, ja toimittajatiedot ovat PRH:n avointa dataa. Niihin sovelletaan kunkin julkaisijan käyttöehtoja. Otsikkokuva on Paimion kaupungin ja peräisin osoitteesta paimio.fi.
