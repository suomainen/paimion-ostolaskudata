// Tekee some-jakokuvan og-kuva.jpg (1200 × 630) repon juureen. Ajo: node tyokalut/tee_og.js
// Kuva on oma, MIT-lisenssillä kuten muukin koodi. Fontti luetaan tiedostosta rubik-latin.woff2.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const fontti = fs.readFileSync(path.join(__dirname, 'rubik-latin.woff2')).toString('base64');
const pylvaat = [42, 47, 47, 17, 25, 21];   // ostot vuosittain, M€ (vain kuvitusta)
const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:Rubik;src:url(data:font/woff2;base64,${fontti}) format('woff2');font-weight:300 900}
*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;font-family:Rubik,sans-serif;color:#fff;background:linear-gradient(135deg,#1a73c4 0%,#0f5ba1 35%,#072b4c 100%);position:relative;overflow:hidden}
.t{position:absolute;left:72px;top:70px;width:700px}
.k{font-size:26px;font-weight:500;color:#ffd166;letter-spacing:.02em}
h1{font-size:76px;line-height:1.05;margin:18px 0 26px;font-weight:600}
p{font-size:30px;line-height:1.4;margin:0;color:#e4ebf5}
.a{position:absolute;left:72px;bottom:56px;font-size:24px;color:#e4ebf5}
.a b{color:#fff;font-weight:500}
.p{position:absolute;right:72px;bottom:120px;height:300px;display:flex;align-items:flex-end;gap:18px}
.p i{display:block;width:46px;border-radius:8px 8px 0 0;background:rgba(255,255,255,.28)}
.p i:last-child{background:#ffd166}
.e{position:absolute;right:86px;top:56px;width:150px;height:150px}
</style><div class="t"><div class="k">Avoin data · 2020–2025</div><h1>Paimion kaupungin ostolaskut</h1><p>Mitä kaupunki ostaa, keneltä ja kuinka paljon.</p></div>
<div class="a"><b>suomainen.github.io/paimion-ostolaskudata</b> · epävirallinen katselusivu</div>
<div class="p">${pylvaat.map(v => `<i style="height:${v / 47 * 100}%"></i>`).join('')}</div>
<svg class="e" viewBox="0 0 64 64"><defs><linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe9a8"/><stop offset="1" stop-color="#ffc233"/></linearGradient></defs><g fill="none" stroke-linecap="round" stroke-width="7"><g stroke="#7a4d00"><path d="M47 22a16 16 0 1 0 0 26M14 33h22M14 41h22"/></g><g stroke="#b37400"><path d="M45.5 20.5a16 16 0 1 0 0 26M12.5 31.5h22M12.5 39.5h22"/></g><g stroke="url(#b)"><path d="M44 19a16 16 0 1 0 0 26M11 30h22M11 38h22"/></g></g></svg>`;
(async () => {
  const selain = await chromium.launch();
  const sivu = await selain.newPage({ viewport: { width: 1200, height: 630 } });
  await sivu.setContent(html); await sivu.waitForTimeout(300);
  await sivu.screenshot({ path: path.join(__dirname, '..', 'og-kuva.jpg'), type: 'jpeg', quality: 90 });
  await selain.close();
})();
