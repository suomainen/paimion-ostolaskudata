#!/usr/bin/env python3
"""
Tekee kartta.json-tiedoston: Suomen kunta- ja maakuntarajat SVG-polkuina.

Ajo:  python tee_kartta.py [vuosi]        (oletus 2025)

Lähde: Tilastokeskuksen avoin rajapinta (geo.stat.fi), yleistetty aineisto 1:4 500 000,
lisenssi CC BY 4.0. Aja uudelleen, kun kuntajako muuttuu, ja päivitä samalla
paivita.py:n LUOKITUS-vuosi.
"""
import json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
WFS = ('https://geo.stat.fi/geoserver/tilastointialueet/wfs?service=WFS&version=2.0.0&request=GetFeature'
       '&typeName=tilastointialueet:{taso}4500k_{vuosi}&outputFormat=json&srsName=EPSG:3067')
TARKKUUS = 500          # metriä per koordinaattiyksikkö
ZOOM_MAAKUNTA = 'Varsinais-Suomi'
ZOOM_REUNUS = 10


def hae(taso, vuosi):
    with urllib.request.urlopen(WFS.format(taso=taso, vuosi=vuosi), timeout=120) as r:
        return json.load(r)['features']


def renkaat(geom):
    if geom['type'] == 'Polygon':
        return geom['coordinates']
    return [r for p in geom['coordinates'] for r in p]


def tee(vuosi):
    kunnat, maakunnat = hae('kunta', vuosi), hae('maakunta', vuosi)
    xs = [x for f in kunnat for r in renkaat(f['geometry']) for x, _ in r]
    ys = [y for f in kunnat for r in renkaat(f['geometry']) for _, y in r]
    x0, y1 = min(xs), max(ys)
    leveys, korkeus = round((max(xs) - x0) / TARKKUUS), round((y1 - min(ys)) / TARKKUUS)

    def pisteet(rengas):
        pts = [(round((x - x0) / TARKKUUS), round((y1 - y) / TARKKUUS)) for x, y in rengas]
        out = [pts[0]]
        for p in pts[1:]:
            if p != out[-1]:
                out.append(p)
        return out

    def polku(geom):
        osat = []
        for r in renkaat(geom):
            p = pisteet(r)
            if len(p) < 4:
                continue
            s = 'M%d %d' % p[0]
            s += 'l' + ' '.join('%d %d' % (x - px, y - py) for (x, y), (px, py) in zip(p[1:], p[:-1])) + 'z'
            osat.append(s)
        return ''.join(osat).replace(' -', '-')

    zoom = next(f for f in maakunnat if f['properties']['nimi'] == ZOOM_MAAKUNTA)
    zp = [p for r in renkaat(zoom['geometry']) for p in pisteet(r)]
    zx, zy = [p[0] for p in zp], [p[1] for p in zp]
    return {
        'w': leveys, 'h': korkeus,
        'vs': [min(zx) - ZOOM_REUNUS, min(zy) - ZOOM_REUNUS,
               max(zx) - min(zx) + 2 * ZOOM_REUNUS, max(zy) - min(zy) + 2 * ZOOM_REUNUS],
        'k': [[f['properties']['nimi'], polku(f['geometry'])] for f in kunnat],
        'm': ''.join(polku(f['geometry']) for f in maakunnat),
    }


if __name__ == '__main__':
    vuosi = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    data = tee(vuosi)
    out = HERE / 'kartta.json'
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'{out.name}: {len(data["k"])} kuntaa, {out.stat().st_size // 1024} kt (vuosi {vuosi})')
