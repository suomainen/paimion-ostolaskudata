# Muutosloki

Versionumero on muotoa **pää.osa.korjaus**: pää = sivun kokonaan uusi versio, osa = uusi ominaisuus tai uuden vuoden aineisto, korjaus = pieni korjaus tai tarkennus. Uusin versio ensin. Pelkkä dokumentaation tai työkalujen muutos ei nosta numeroa.

## 2.2.2

- Kehitys-välilehden listojen otsikot ja saatteet muotoiltu niin, etteivät ne näytä väitteiltä yksittäisistä toimittajista: Toimittajat, joilta ostettiin eniten (aiemmin Suuret toimittajat) ja Yhteiset toimittajat (aiemmin Sama toimittaja usealla toimielimellä).
- Varaus on listan yläpuolella, ja viittaus hankintojen kynnysarvoihin siirtyi Ohje-välilehdelle. Listan oletusraja on 100 000 euroa (aiemmin 60 000).
- Yhteiset toimittajat -listaa ei näytetä vuodelta, jonka toimielin on arvioitu (2025).

## 2.2.1

- Näkymän vaihto vierittää sivun alkuun, jolloin uusi näkymä alkaa aina ylhäältä.

## 2.2.0

- Rauhallisempi ulkoasu: fonttikokoja on viisi (aiemmin 16) ja lihavuuksia kaksi, korttien väleissä ja sisällä on enemmän tilaa ja taulukon rivit ovat korkeampia.
- Harmaa tausta poistettu tunnusluvuista, hakukentistä ja valikoista: kortit ja kentät ovat valkoisia ohuella reunalla, ja sivun tausta on hennon sinertävä. Korteista poistettu varjo.
- Tunnuslukuja on neljä (ostot, toimittajat, paimiolaisten ja Varsinais-Suomen osuus); tositteet, rivit, keskimääräinen rivi, toimialat ja tilit ovat pienenä rivinä niiden alla.
- Sivupalkin näkymistä valittu on sininen ja muut pelkkää tekstiä.
- Puukartan laatikot ovat sinisen sävyjä suurimmasta pienimpään.
- Kapean näytön valikossa ovat myös näkymät Yhteenveto, Kehitys ja Toimittaja.
- Toimielimet ja Tiliryhmät ovat omina kortteinaan, ja selitteistä on poistettu toistuva Napsauta rajataksesi.

## 2.1.0

- Yläpalkin vasemmassa reunassa on sivuston nimi Paimion ostolaskudata, joka vie aloitukseen: ohje, uusin vuosi, ei rajauksia.
- Sininen otsikkopalkki näkyy vain aloituksessa (Ohje). Muissa näkymissä sisältö alkaa heti yläpalkin alta.
- Kysy ja ehdota on oma osionsa ennen Tietoa aineistosta -osiota, ja siinä on linkki tekijän sivulle summanen.org.
- Toimittaja-välilehdellä haun vieressä on painike Tyhjennä ja hae uudestaan.
- Yläpalkin linkeistä poistettu näkymät, koska ne ovat sivupalkissa. Jäljellä ovat Ohje, Tietoa aineistosta ja Lähdekoodi.

## 2.0.0

- Uusi asettelu: näkymät, vuosi ja kaikki rajaukset ovat vasemman reunan sivupalkissa, joka pysyy näkyvissä sivua vieritettäessä. Sisältö on oikealla.
- Sivupalkissa on valikot myös toimialalle, kunnalle, yritysmuodolle ja palveluluokalle, ja valitut rajaukset näkyvät kohdassa Valittuna.
- Puhelimella ja kapealla näytöllä rajaukset avautuvat alhaalta Rajaa-painikkeesta, joka näyttää voimassa olevien rajausten määrän. Vuoden voi vaihtaa sen vierestä.
- Iso otsikkokuva näkyy vain Ohje-näkymässä; muissa näkymissä otsikko on kapea palkki.
- Sivu käyttää leveän näytön koko leveyden (enintään 1640 px).

## 1.10.0

- Ohje on ensimmäinen välilehti ja avautuu oletuksena. Sen alussa kerrotaan, miksi sivu on tehty ja kenelle, ja pyydetään kysymyksiä ja parannusehdotuksia.
- Linkit, joissa on rajauksia mutta ei näkymää, avaavat edelleen yhteenvedon. Näkymä kirjoitetaan nyt aina osoitteeseen.

## 1.9.0

- Ohje omana välilehtenään: pikaopas, näkymät, rajaaminen, toimittajan tiedot, taulukot ja kaaviot, esimerkkikysymyksiä, käsitteet, lukujen tulkinta sekä kieli, ulkoasu ja näppäimistökäyttö. Suomeksi, ruotsiksi ja englanniksi.
- Puukartta on oletusnäkymä tileille, tulosalueille, palveluluokille ja toimialoille, ja laatikot ovat erivärisiä.
- Toimittajan tyyppi näytetään oletuksena osuuksina.
- Selaimen Takaisin-painike (myös hiiren sivupainike) palauttaa edellisen näkymän: jokainen valinta on oma askeleensa selaimen historiassa.
- Toimittaja-välilehdellä valitun vuoden saa pois merkistä tai painikkeesta Näytä kaikki vuodet, ja toimittajan voi vaihtaa painikkeesta Valitse toinen toimittaja.
- Sivukuvake (euromerkki) ja some-jaon tiedot: kuvaus, Open Graph -tiedot ja jakokuva `og-kuva.jpg` sekä `llms.txt` ja `sitemap.xml`.
- Yläpalkin linkeistä poistettu Lähdeaineisto (linkki on edelleen sivun alussa ja lopussa), jotta linkit mahtuvat näkyviin.

## 1.8.0

- Esitystavan valinta osioittain: tilit, tulosalueet, palveluluokat ja toimialat taulukkona tai puukarttana, toimittajat taulukkona tai kymmenen suurimman kaaviona, toimittajan tyyppi luettelona tai osuuksina (osuus toimittajista ja euroista rinnakkain). Valinta tallentuu linkkiin (`kaavio=`).
- Uudet jaottelut: yritysmuoto (myös rajauksena) ja tiliryhmät rengaskaaviona tai taulukkona.
- Toimittajataulukkoon sarakkeet tyyppi ja toimiala, tunnuslukuihin toimialojen ja käytössä olevien tilien määrä.
- Kehitys: Suuret toimittajat (vuoden ostot vähintään valitun rajan verran) ja Sama toimittaja usealla toimielimellä.
- Tietoa aineistosta -osioon kohta Mihin ostolaskudataa voi käyttää.
- Versionumero näkyy yläpalkissa.
- Toimittaja-välilehdellä voi valita vuoden pylväästä tai valikosta: näkyviin tulevat vuoden kuukaudet ja laskurivit (`tvuosi=`).
- Napsautettavat rivit erottuvat: nimi on korostettu ja rivin lopussa on kuvake (nuoli avaa toimittajan laskurivit, suppilo rajaa raportin). Sivun alussa on kuitattava vinkki.
- Taulukoiden vaakavieritys poistettu: sarakkeet tiivistetty, kapealla näytöllä näytetään vain tärkeimmät sarakkeet ja leveät taulukot saavat koko rivin.

## 1.7.0

- Kolme välilehteä sivun alussa: Yhteenveto, Kehitys (aiemmin Analyysit) ja Toimittaja. Vanhat linkit `nakyma=analyysit` toimivat edelleen.
- Kehitys: viivakaavio valituista riveistä (oletuksena viisi suurinta, taulukon valintaruuduilla enintään kuusi), trendiviiva jokaisella rivillä sekä kaaviot paikallisuudesta ja keskittyneisyydestä ja uusien ja poistuneiden toimittajien määrästä vuosittain. Sote-siirto 2023 on merkitty kaavioihin.
- Toimittaja: yhden toimittajan koko historia rajauksista riippumatta. Haku nimellä tai Y-tunnuksella, ostot vuosittain ja kuukausittain koko jaksolta, sijoitus ja osuus kaikista ja toimialan ostoista vuosittain, tilit ja toimielimet vuosittain sekä kaikki laskurivit. Näkymällä on pysyvä linkki (`nakyma=toimittaja&toimittaja=Y-tunnus`), ja toimittajan pikakatselusta pääsee siihen painikkeella Näytä koko historia.
- Korjaus: taulukon sisällä oleva ruudunlukijateksti saattoi aiheuttaa vaakavierityksen kapealla näytöllä.

## 1.6.0

- Sivu myös ruotsiksi ja englanniksi: kielipainikkeet FI, SV ja EN yläpalkissa. Valinta muistetaan selaimessa ja kulkee linkin mukana (`kieli=sv` tai `kieli=en`). Käännökset ovat epävirallisia; aineiston omat arvot (tilit, toimialat, palveluluokat, toimielimet, tulosalueet) näytetään suomeksi ja merkitään suomenkielisiksi ruudunlukijalle.
- Tumman ulkoasun vaihdin yläpalkissa. Oletus on vaalea, ja valinta muistetaan selaimessa. Kartan väriasteikko kääntyy tummassa ulkoasussa.
- Navigaatio yläpalkin oikeaan reunaan: Yhteenveto, Analyysit, Tietoa aineistosta, Lähdeaineisto ja Lähdekoodi. Kapealla näytöllä linkit ovat valikkopainikkeen takana.
- Sivun sisäiset linkit eivät enää hävitä näkymän tilaa osoitteesta.

## 1.5.1

- Kopioi linkki tähän näkymään -painike siirretty yläpalkkiin, joka pysyy näkyvissä sivua vieritettäessä.
- Yhteenveto- ja Analyysit-välilehdet isompina valintoina kuvauksineen.

## 1.5.0

- Analyysit-välilehti: kehitys vuosittain valitulla jaottelulla (toimiala, tili, palveluluokka, toimielin, kunta, maakunta, toimittajan tyyppi), uudet ja poistuneet toimittajat, paikallisuus tileittäin, toimittajat ostojen koon mukaan sekä paikallisuus ja keskittyneisyys vuosittain.
- Pysyvät linkit: näkymän osoitteessa on nyt vuosi, nimet ja koodit järjestysnumeroiden sijaan, joten linkki vie samaan näkymään myös aineiston päivityksen jälkeen. Osoitteeseen tallentuvat myös välilehti, jaottelu, mittarivalinnat, kartan alue ja avattu toimittaja.
- Kopioi linkki näkymään -painike.
- Selaintarkistus `tyokalut/tarkista_sivu.js`: saavutettavuus (axe), näppäimistökäyttö, linkkien pysyvyys ja analyysien luvut.

## 1.4.0

- Saavutettavuus WCAG 2.1 AA -tasolle: ohituslinkki sisältöön, näkyvä kohdistus, taulukoiden lajittelu ja rivien valinta painikkeina, toimittajan tiedot modaalisena ikkunana, kartalle tekstivaihtoehto (Kunta-valikko), tilaviesti ruudunlukijalle näkymän päivittyessä ja maininta uuteen välilehteen avautuvista linkeistä.
- Kontrastit: himmennetty teksti tummemmaksi, kohdistuskehys tummansiniseksi, kartan kuntarajoille ja himmennetyille pylväille erottuva reuna.
- Tekoälyhuomautus sivun huomioihin ja alatunnisteeseen sekä yhteystiedot korjauksia varten.
- Alatunnisteeseen tekijä, summanen.org, lähdekoodilinkki ja versionumero.
- Liikkeen vähentäminen käyttöjärjestelmän asetuksen mukaan.

## 1.3.0

- Palveluluokat: uusi taulukko ja rajaus (Valtiokonttorin kuntien yhteinen luokitus, aineistossa vuodesta 2022).
- Korjaus: 168 kotimaista toimittajaa oli merkitty ulkomaisiksi, koska maakoodi puuttuu vuosien 2020–2021 aineistosta.
- Arviointimenetelmän takautuva testi ajetaan jokaisella päivityksellä, ja tulokset näkyvät sivun huomioissa. Mukana nyt myös tulosalueen osuvuus.
- Hyvitysten määrä näkyy Ostot yhteensä -luvun alla. Negatiiviselle summalle ei näytetä palkkia eikä prosenttiosuutta.
- Kartan yhteyteen huomautus: kotikunta on yrityksen rekisteröity osoite.
- Otsikkokuva tehdään koodilla; kaupungin kuva poistettu.
- Koontiskripti jaettu funktioihin, lisätty testit, `tee_kartta.py`, `requirements.txt` ja `tunnistamattomat.csv`. PRH-tiedot haetaan uudelleen vuoden välein, ja uudet vuodet löytyvät kaupungin sivulta automaattisesti.

## 1.2.0

- Vuodelle 2025 toimielimet ja tulosalueet arvioituna palveluluokan perusteella. Arvioidut rivit merkitty.

## 1.1.0

- Suomen kuntakartta: kunnat väritetty ostosumman tai toimittajamäärän mukaan, rajaus koko Suomeen tai Varsinais-Suomeen, kunnan valinta rajaa raportin.
- Kuukausirajaus kaaviosta tai valikosta.
- Päivitystyökalut (`tyokalut/`) ja aloitteen tausta README:hen.

## 1.0.0

- Ensimmäinen julkaisu: ostot vuosilta 2020–2025, tunnusluvut, kaaviot, toimittajahaku ja rajaukset. Toimittajatiedot rikastettu PRH:n YTJ-rajapinnasta.
