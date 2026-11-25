# Muutosloki

Versionumero on muotoa **pää.osa.korjaus**: pää = sivun kokonaan uusi versio, osa = uusi ominaisuus tai uuden vuoden aineisto, korjaus = pieni korjaus tai tarkennus. Uusin versio ensin. Pelkkä dokumentaation tai työkalujen muutos ei nosta numeroa.

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
