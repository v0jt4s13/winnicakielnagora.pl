// Testy logiki cen i renderu karty. Uruchomienie: node tools/test-produkty.js
// Node nie jest zaleznoscia witryny - to opcjonalne narzedzie deweloperskie.
const fs = require("fs");
const Produkty = eval(fs.readFileSync(__dirname + "/../assets/js/produkty.js", "utf8") + ";Produkty");

let bledy = 0;
const sprawdz = (opis, warunek) => {
  console.log(`${warunek ? "OK  " : "BLAD"}  ${opis}`);
  if (!warunek) bledy++;
};

// promocja: brutto 58.50 przy rabacie 10% => przed rabatem 65.00, netto 47.56
const promo = { id: "monarch-2023", nazwa: "Monarch", odmiany_slug: ["monarch"], kategoria: "Czerwone",
  rocznik: 2023, alkohol: 12.5, pojemnosc_ml: 750, cena_brutto: 58.50, rabat_procent: 10,
  dostepne: true, opis: "Wyraziste czerwone.", zdjecie: "monarch-kieliszek-01" };
const c = Produkty.policzCeny(promo, 0.23);
sprawdz("netto = brutto / 1.23", Math.abs(c.netto - 58.50 / 1.23) < 1e-9);
sprawdz("cena sprzed rabatu = 65.00", Math.abs(c.przedRabatem - 65) < 1e-9);
sprawdz("promocja rozpoznana", c.promocja === true);

const html = Produkty.renderProductCard(promo, 0.23);
sprawdz("badge -10%", html.includes(">-10%<"));
sprawdz("przekreslona cena 65.00 zl", html.includes("line-through") && html.includes("65.00 zł"));
sprawdz("cena promocyjna w text-ring", html.includes('text-3xl font-bold text-ring">58.50 zł'));
sprawdz("netto wyliczone", html.includes('netto-cena text-muted-foreground"><span class="netto-etykieta">netto:</span> 47.56 zł'));
sprawdz("data-price z brutto", html.includes('data-price="58.50"'));
sprawdz("data-promo=true", html.includes('data-promo="true"'));
sprawdz("brak martwych atrybutow", !html.includes("data-price-net") && !html.includes("data-discount"));
sprawdz("link do strony odmiany", html.includes('href="./wina/monarch.html"'));
const dwa = Produkty.renderProductCard({ ...promo, odmiany_slug: ["monarch", "seyval-blanc"] }, 0.23);
sprawdz("dwa chipy szczepu z linkami",
  dwa.includes('href="./wina/monarch.html"') && dwa.includes('href="./wina/seyval-blanc.html"') &&
  dwa.includes(">Seyval Blanc</a>"));
for (const [nazwa, wino] of [["brak pola", { ...promo, odmiany_slug: undefined }], ["pusta lista", { ...promo, odmiany_slug: [] }]]) {
  const h = Produkty.renderProductCard(wino, 0.23);
  sprawdz(`${nazwa}: brak wiersza szczepu`, !h.includes("Szczep:") && !h.includes("chip-link"));
}
sprawdz("miniatura -sm", html.includes("monarch-kieliszek-01-sm.jpg"));

const butelka = { ...promo, zdjecie_sklep: "butelki/dziki_owoc-monarch-2024-czerwone-polwytrawne.jpg" };
const htmlButelka = Produkty.renderProductCard(butelka, 0.23);
sprawdz("bezpośrednie zdjęcie butelki",
  htmlButelka.includes("attached_assets/butelki/dziki_owoc-monarch-2024-czerwone-polwytrawne.jpg"));

// bez promocji
const zwykle = { ...promo, id: "x", rabat_procent: 0, cena_brutto: 59 };
const html2 = Produkty.renderProductCard(zwykle, 0.23);
sprawdz("bez promocji: brak przekreslenia", !html2.includes("line-through"));
sprawdz("bez promocji: cena w text-foreground", html2.includes("text-3xl font-bold text-foreground"));
sprawdz("bez promocji: data-promo=false", html2.includes('data-promo="false"'));

// sok bez rocznika i alkoholu
const sok = { id: "sok", nazwa: "Sok z białych winogron", odmiany_slug: ["soki"], kategoria: "Soki",
  pojemnosc_ml: 500, cena_brutto: 18, rabat_procent: 0, dostepne: true, opis: "100% soku.",
  zdjecie: "winnica-butelka-biale-01" };
const html3 = Produkty.renderProductCard(sok, 0.23);
sprawdz("sok: brak 'Rocznik'", !html3.includes("Rocznik"));
sprawdz("sok: brak '% alk.'", !html3.includes("alk."));
sprawdz("sok: brak wiersza szczepu", !html3.includes("Szczep:") && !html3.includes("chip-link"));
sprawdz("1000 ml jako 1 l", Produkty.opisPodtytul({ pojemnosc_ml: 1000 }).includes("1 l"));
sprawdz("1500 ml jako 1,5 l", Produkty.opisPodtytul({ pojemnosc_ml: 1500 }).includes("1,5 l"));
sprawdz("999 ml zostaje w ml", Produkty.opisPodtytul({ pojemnosc_ml: 999 }).includes("999 ml"));
sprawdz("sok: pojemnosc widoczna", html3.includes("500 ml"));

// ucieczka znakow specjalnych w danych z pliku
const zlosliwe = { ...promo, id: "y", nazwa: '<script>alert(1)</script>' };
sprawdz("HTML w danych jest escapowany",
  !Produkty.renderProductCard(zlosliwe, 0.23).includes("<script>alert"));

// przycisk koszyka wylaczany dla podgladu w panelu
sprawdz("podglad bez przycisku koszyka",
  !Produkty.renderProductCard(promo, 0.23, { przyciskKoszyka: false }).includes("data-add-to-cart"));

console.log(bledy === 0 ? "\nWSZYSTKIE TESTY PRZESZLY" : `\n${bledy} TESTOW NIE PRZESZLO`);
process.exit(bledy === 0 ? 0 : 1);
