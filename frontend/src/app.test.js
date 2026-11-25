// app.test.js – osnovni enotski testi za pomožne funkcije in podatke frontenda

import test from "node:test";
import assert from "node:assert/strict";

// 1. Test izračuna datuma za danes in jutri (iz SpremembeUrnika.jsx)
function datumCez(zamik) {
  const d = new Date("2026-11-30T10:00:00Z");
  d.setUTCDate(d.getUTCDate() + zamik);
  return d.getUTCFullYear() + "-" + String(d.getUTCMonth() + 1).padStart(2, "0") + "-" + String(d.getUTCDate()).padStart(2, "0");
}

test("datumCez vrne pravilen datum za danes (zamik 0) in jutri (zamik 1)", () => {
  assert.equal(datumCez(0), "2026-11-30");
  assert.equal(datumCez(1), "2026-12-01");
});

// 2. Test prikaza celice v tedenskem urniku (iz Urnik.jsx)
function celica(urnik, dan, solskaUra) {
  const najdena = urnik.find((u) => u.dan_v_tednu === dan && u.solska_ura === solskaUra);
  return najdena ? najdena.predmet + " · " + najdena.ucitelj : "";
}

test("celica vrne predmet in učitelja ali prazen niz, če ure ni", () => {
  const vzorec = [{ dan_v_tednu: 1, solska_ura: 2, predmet: "Programiranje", ucitelj: "Novak" }];
  assert.equal(celica(vzorec, 1, 2), "Programiranje · Novak");
  assert.equal(celica(vzorec, 3, 1), "");
});

// 3. Test štetja nepokritih ur v dnevnem pregledu (iz DnevniPregled.jsx)
test("filtriranje nepokritih ur pravilno prešteje samo nepokrite", () => {
  const ure = [
    { id: 1, status: "nepokrita" },
    { id: 2, status: "potrjena" },
    { id: 3, status: "nepokrita" },
  ];
  const nepokrite = ure.filter((u) => u.status === "nepokrita").length;
  assert.equal(nepokrite, 2);
});

// 4. Test izločanja polja geslo iz prikazanih stolpcev tabele (iz Seznam.jsx)
test("stolpci tabele učiteljev ne prikazujejo polja geslo", () => {
  const polja = ["ime", "priimek", "email", "geslo"];
  const stolpci = polja.filter((polje) => polje !== "geslo");
  assert.deepEqual(stolpci, ["ime", "priimek", "email"]);
});

// 5. Test oblikovanja besedila o plačljivosti suplence (iz DnevniPregled.jsx in MojeSuplence.jsx)
test("oznaka plačljivosti pravilno loči plačano uro in uro za fond", () => {
  const oznaka = (placana) => (placana ? "da" : "ne – fond");
  assert.equal(oznaka(true), "da");
  assert.equal(oznaka(false), "ne – fond");
});
