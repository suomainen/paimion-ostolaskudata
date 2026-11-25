#!/usr/bin/env python3
"""
Tekee otsikkokuvan hero.svg: abstrakti pylväskuvio sivun väreissä.

Ajo:  python tee_kuva.py

Kuva syntyy kokonaan tästä koodista (kiinteä satunnaissiemen), joten se kuuluu
repon MIT-lisenssin piiriin eikä sisällä kenenkään muun aineistoa.
"""
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 1600, 520
NAVY, BLUE, LIGHT, YELLOW = '#072b4c', '#0f5ba1', '#6f9ccf', '#ffd166'
SIEMEN = 2025


def tee():
    rnd = random.Random(SIEMEN)
    osat = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
        '<defs>',
        f'<linearGradient id="tausta" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/>'
        f'<stop offset="1" stop-color="{BLUE}"/></linearGradient>',
        '<linearGradient id="haive" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>',
        '<mask id="oikea"><rect width="100%" height="100%" fill="url(#haive)"/></mask>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="url(#tausta)"/>',
        '<g mask="url(#oikea)">',
    ]
    # vaakaviivasto
    for i in range(1, 6):
        y = H - i * 80
        osat.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#fff" stroke-opacity=".07"/>')
    # kaksi pylväskerrosta: taaempi vaalea, etummainen sininen, muutama keltainen korostus
    for kerros, (vari, alfa, leveys, vali) in enumerate([(LIGHT, .16, 46, 18), ('#ffffff', .22, 30, 34)]):
        x, taso = 40 + kerros * 23, rnd.uniform(.3, .6)
        while x < W:
            taso = min(.95, max(.12, taso + rnd.uniform(-.16, .17)))
            h = round(taso * (H - 90))
            korostus = kerros == 1 and rnd.random() < .09
            osat.append(f'<rect x="{x}" y="{H - h}" width="{leveys}" height="{h}" rx="5" '
                        f'fill="{YELLOW if korostus else vari}" fill-opacity="{.75 if korostus else alfa}"/>')
            x += leveys + vali
    osat.append('</g></svg>')
    return ''.join(osat)


if __name__ == '__main__':
    out = HERE / 'hero.svg'
    out.write_text(tee(), encoding='utf-8')
    print(f'{out.name}: {out.stat().st_size} tavua')
