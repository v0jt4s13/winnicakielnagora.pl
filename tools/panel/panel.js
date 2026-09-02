/**
 * Panel redakcyjny cennika. Działa wyłącznie z tools/panel/serwer.py na 127.0.0.1.
 *
 * Podgląd karty renderuje Produkty.renderProductCard() z assets/js/produkty.js —
 * tym samym kodem, co sklep. Dzięki temu podgląd nie może się rozjechać z witryną.
 * Bez alert()/confirm(): blokują automatyzację przeglądarki (.ai/GUARDRAILS.md).
 */
const qs = (sel) => document.querySelector(sel);
const qsa = (sel) => Array.from(document.querySelectorAll(sel));

const POLA_LICZBOWE = ["rocznik", "alkohol", "pojemnosc_ml", "cena_brutto", "rabat_procent"];
const POLA_OPCJONALNE = ["rocznik", "alkohol"];

let cennik = null;
let zdjecia = [];
let odmiany = [];
let wybrany = null; // indeks edytowanej pozycji
let zmienione = false;

// --- komunikaty -----------------------------------------------------------

function pokazKomunikat(tresc, rodzaj = "") {
  const el = qs("#komunikat");
  el.className = `komunikat ${rodzaj}`.trim();
  el.innerHTML = tresc;
  el.hidden = false;
}

function ukryjKomunikat() {
  qs("#komunikat").hidden = true;
}

function oznaczZmiane(stan = true) {
  zmienione = stan;
  qs("#stan-zmian").textContent = stan ? "● niezapisane zmiany" : "";
}

// --- wczytanie ------------------------------------------------------------

async function wczytaj() {
  try {
    const odp = await fetch("api/wczytaj");
    const dane = await odp.json();
    if (!odp.ok) throw new Error(dane.komunikat || `HTTP ${odp.status}`);
    cennik = dane.cennik;
    zdjecia = dane.zdjecia;
    odmiany = dane.odmiany;
    qs("#sciezka").textContent = dane.sciezka;
    if (odmiany.length === 0) {
      pokazKomunikat("Nie znaleziono żadnej strony odmiany w katalogu <code>wina/</code>. " +
        "Pozycji nie da się zapisać, dopóki nie ma do czego linkować.", "ostrzezenie");
    }
    renderWszystko();
  } catch (blad) {
    // Najczestszy przypadek: zamiast JSON-a przyszedl HTML, czyli pod adresem api/
    // nie ma trasy i odpowiedzial serwer plikow albo strona bledu.
    const zamiastJson = /Unexpected token|not valid JSON|<!doctype/i.test(blad.message);
    const lokalnie = ["localhost", "127.0.0.1"].includes(location.hostname);
    let rada;
    if (!zamiastJson) {
      rada = "";
    } else if (lokalnie) {
      rada =
        "<br>Wygląda na to, że otworzyłeś panel przez zwykły serwer plików. Uruchom " +
        "<code>python3 tools/panel/serwer.py</code> i wejdź na <code>http://127.0.0.1:8765</code>.";
    } else {
      rada =
        `<br>Adres <code>${location.pathname.replace(/panel\.html$/, "api/wczytaj")}</code> ` +
        "zwrócił stronę HTML zamiast danych, czyli aplikacja nie obsłużyła tej trasy. " +
        "Sprawdź, czy serwer uruchamia aktualne <code>wsgi.py</code> i czy został przeładowany " +
        "po ostatnim wdrożeniu. Panel na produkcji <strong>nie potrzebuje</strong> " +
        "<code>tools/panel/serwer.py</code> — API jest w <code>wsgi.py</code>.";
    }
    pokazKomunikat(`Nie udało się wczytać cennika: ${Produkty.escape(blad.message)}${rada}`, "blad");
  }
}

// --- lista pozycji --------------------------------------------------------

function renderLista() {
  const lista = qs("#lista");
  const wina = cennik.wina;
  qs("#licznik").textContent = wina.length ? `(${wina.length})` : "";
  qs("#pusto").hidden = wina.length > 0;

  lista.innerHTML = wina
    .map((wino, i) => {
      const ceny = Produkty.policzCeny(wino, cennik.stawka_vat);
      const znacznik = wino.dostepne === false
        ? '<span class="kropka niedostepna">○ niedostępne</span>'
        : '<span class="kropka dostepna">● dostępne</span>';
      const promo = ceny.promocja
        ? `<span class="kropka promocja">-${wino.rabat_procent}%</span>`
        : "";
      return `
        <li data-indeks="${i}" class="${i === wybrany ? "wybrana" : ""}">
          <span class="nazwa">${Produkty.escape(wino.nazwa || "(bez nazwy)")}</span>
          <span class="meta">${Produkty.escape(wino.kategoria || "—")}</span>
          <span class="meta cena">${Produkty.formatujCene(ceny.brutto)}</span>
          ${promo}
          ${znacznik}
        </li>`;
    })
    .join("");
}

function renderKategorie() {
  qs("#lista-kategorii").innerHTML = (cennik.kategorie || [])
    .map(
      (nazwa) => `<li>${Produkty.escape(nazwa)}
        <button type="button" data-kategoria="${Produkty.escape(nazwa)}" title="Usuń">×</button></li>`
    )
    .join("");
}

function renderWszystko() {
  renderLista();
  renderKategorie();
  if (wybrany !== null) renderFormularz();
}

// --- formularz ------------------------------------------------------------

function opcje(wartosci, wybrana) {
  return ['<option value="">— wybierz —</option>']
    .concat(
      wartosci.map(
        (w) => `<option value="${Produkty.escape(w)}"${w === wybrana ? " selected" : ""}>${Produkty.escape(w)}</option>`
      )
    )
    .join("");
}

function renderFormularz() {
  const wino = cennik.wina[wybrany];
  qs("#sekcja-formularza").hidden = false;
  qs("#tytul-formularza").textContent = wino.nazwa || "Nowa pozycja";

  const f = qs("#formularz");
  f.elements.odmiana_slug.innerHTML = opcje(odmiany, wino.odmiana_slug);
  f.elements.kategoria.innerHTML = opcje(cennik.kategorie || [], wino.kategoria);
  f.elements.zdjecie.innerHTML = opcje(zdjecia, wino.zdjecie);

  ["nazwa", "id", "opis", ...POLA_LICZBOWE].forEach((pole) => {
    const wartosc = wino[pole];
    f.elements[pole].value = wartosc === undefined || wartosc === null ? "" : wartosc;
  });
  f.elements.dostepne.checked = wino.dostepne !== false;

  renderPodglad();
}

function renderPodglad() {
  const wino = cennik.wina[wybrany];
  qs("#podglad-karty").innerHTML = Produkty.renderProductCard(wino, cennik.stawka_vat, {
    przyciskKoszyka: false,
    linkOdmiany: false,
    bazaZdjec: "../../attached_assets/photos/",
  });
}

/** Przepisuje formularz do modelu. Puste pola opcjonalne znikają z JSON-a. */
function zbierzFormularz() {
  const f = qs("#formularz");
  const wino = cennik.wina[wybrany];

  ["nazwa", "id", "opis", "odmiana_slug", "kategoria", "zdjecie"].forEach((pole) => {
    wino[pole] = f.elements[pole].value.trim();
  });
  POLA_LICZBOWE.forEach((pole) => {
    const surowa = f.elements[pole].value.trim();
    if (surowa === "" && POLA_OPCJONALNE.includes(pole)) delete wino[pole];
    else wino[pole] = surowa === "" ? 0 : Number(surowa);
  });
  wino.dostepne = f.elements.dostepne.checked;
}

// --- walidacja w przeglądarce (serwer i tak sprawdza jeszcze raz) ---------

function bledyPozycji(wino, indeks) {
  const bledy = [];
  const dodaj = (pole, komunikat) => bledy.push({ pole, komunikat });

  if (!/^[a-z0-9-]+$/.test(wino.id || "")) dodaj("id", "Małe litery, cyfry i myślnik");
  else if (cennik.wina.some((inne, i) => i !== indeks && inne.id === wino.id))
    dodaj("id", "Ten identyfikator już występuje");
  if (!wino.nazwa) dodaj("nazwa", "Pole wymagane");
  if (!wino.opis) dodaj("opis", "Pole wymagane");
  if (!wino.odmiana_slug) dodaj("odmiana_slug", "Wybierz stronę odmiany");
  if (!(cennik.kategorie || []).includes(wino.kategoria)) dodaj("kategoria", "Wybierz kategorię");
  if (!zdjecia.includes(wino.zdjecie)) dodaj("zdjecie", "Wybierz zdjęcie");
  if (!(wino.cena_brutto > 0)) dodaj("cena_brutto", "Cena musi być większa od zera");
  else if (Math.round(wino.cena_brutto * 100) / 100 !== wino.cena_brutto)
    dodaj("cena_brutto", "Najwyżej dwa miejsca po przecinku");
  if (!(wino.rabat_procent >= 0 && wino.rabat_procent <= 99))
    dodaj("rabat_procent", "Rabat od 0 do 99");
  if (!(wino.pojemnosc_ml > 0)) dodaj("pojemnosc_ml", "Podaj pojemność");
  return bledy;
}

function pokazBledyPola(bledy) {
  qsa("#formularz label").forEach((label) => {
    label.classList.remove("niepoprawne");
    label.querySelector(".blad-pola")?.remove();
  });
  bledy.forEach(({ pole, komunikat }) => {
    const kontrolka = qs("#formularz").elements[pole];
    const label = kontrolka?.closest("label");
    if (!label) return;
    label.classList.add("niepoprawne");
    const info = document.createElement("span");
    info.className = "blad-pola";
    info.textContent = komunikat;
    label.appendChild(info);
  });
}

// --- zapis ----------------------------------------------------------------

async function zapisz() {
  const wszystkie = cennik.wina.flatMap((wino, i) =>
    bledyPozycji(wino, i).map((b) => ({ ...b, indeks: i, nazwa: wino.nazwa }))
  );
  if (wszystkie.length > 0) {
    pokazKomunikat(
      "Nie zapisano — popraw błędy:<ul>" +
        wszystkie
          .map((b) => `<li>${Produkty.escape(b.nazwa || `pozycja ${b.indeks + 1}`)}: ${Produkty.escape(b.komunikat)} (${b.pole})</li>`)
          .join("") +
        "</ul>",
      "blad"
    );
    if (wybrany !== null) pokazBledyPola(bledyPozycji(cennik.wina[wybrany], wybrany));
    return;
  }

  qs("#zapisz").disabled = true;
  try {
    const odp = await fetch("api/zapisz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cennik),
    });
    const wynik = await odp.json();
    if (!odp.ok) {
      const lista = (wynik.bledy || [])
        .map((b) => `<li>${b.pozycja === null ? "cały plik" : `pozycja ${b.pozycja + 1}`}: ${Produkty.escape(b.komunikat)}</li>`)
        .join("");
      pokazKomunikat(`Serwer odrzucił zapis:<ul>${lista}</ul>`, "blad");
      return;
    }
    oznaczZmiane(false);
    pokazKomunikat(
      `✓ Zapisano ${wynik.pozycji} pozycji. Kopia poprzedniej wersji: <code>${wynik.kopia}</code>.<br>` +
        "Pamiętaj o commicie i wdrożeniu — panel niczego nie publikuje.",
      "sukces"
    );
  } catch (blad) {
    pokazKomunikat(`Nie udało się zapisać: ${blad.message}`, "blad");
  } finally {
    qs("#zapisz").disabled = false;
  }
}

// --- propozycja identyfikatora -------------------------------------------

const ZNAKI = { ą: "a", ć: "c", ę: "e", ł: "l", ń: "n", ó: "o", ś: "s", ź: "z", ż: "z" };

function proponujId(nazwa, rocznik) {
  const podstawa = (nazwa || "")
    .toLowerCase()
    .replace(/[ąćęłńóśźż]/g, (z) => ZNAKI[z])
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  const zRocznikiem = rocznik ? `${podstawa}-${rocznik}` : podstawa;
  let kandydat = zRocznikiem || "pozycja";
  let n = 2;
  while (cennik.wina.some((w, i) => i !== wybrany && w.id === kandydat)) {
    kandydat = `${zRocznikiem}-${n++}`;
  }
  return kandydat;
}

// --- zdarzenia ------------------------------------------------------------

qs("#lista").addEventListener("click", (e) => {
  const li = e.target.closest("li[data-indeks]");
  if (!li) return;
  wybrany = Number(li.dataset.indeks);
  renderLista();
  renderFormularz();
  ukryjKomunikat();
});

qs("#dodaj").addEventListener("click", () => {
  cennik.wina.push({
    id: "", nazwa: "", odmiana_slug: "", kategoria: cennik.kategorie?.[0] || "",
    pojemnosc_ml: 750, cena_brutto: 0, rabat_procent: 0, dostepne: true,
    opis: "", zdjecie: "",
  });
  wybrany = cennik.wina.length - 1;
  oznaczZmiane();
  renderLista();
  renderFormularz();
});

qs("#usun").addEventListener("click", () => {
  if (wybrany === null) return;
  const [usuniete] = cennik.wina.splice(wybrany, 1);
  wybrany = null;
  qs("#sekcja-formularza").hidden = true;
  oznaczZmiane();
  renderLista();
  pokazKomunikat(`Usunięto „${Produkty.escape(usuniete.nazwa || "pozycję")}”. Zmiana zostanie utrwalona po zapisie.`, "ostrzezenie");
});

qs("#formularz").addEventListener("input", (e) => {
  if (wybrany === null) return;
  const f = qs("#formularz");

  // Identyfikator proponujemy tylko dopóki użytkownik go sam nie tknął.
  if (e.target.name === "nazwa" && !f.elements.id.dataset.reczny) {
    f.elements.id.value = proponujId(f.elements.nazwa.value, f.elements.rocznik.value);
  }
  if (e.target.name === "id") f.elements.id.dataset.reczny = "1";

  zbierzFormularz();
  oznaczZmiane();
  renderPodglad();
  renderLista();
  pokazBledyPola(bledyPozycji(cennik.wina[wybrany], wybrany));

  // Zdjęcia z członem "-osoby-" pokazują rozpoznawalne osoby, a zgody na wizerunek
  // nie są jeszcze potwierdzone (TODO.md #14).
  if (e.target.name === "zdjecie" && e.target.value.includes("-osoby-")) {
    pokazKomunikat(
      "Na tym zdjęciu są rozpoznawalne osoby, a zgody na wizerunek nie są jeszcze potwierdzone. " +
        "Wybierz kadr bez osób albo najpierw potwierdź zgodę.",
      "ostrzezenie"
    );
  }
});

qs("#dodaj-kategorie").addEventListener("click", () => {
  const pole = qs("#nowa-kategoria");
  const nazwa = pole.value.trim();
  if (!nazwa) return;
  if ((cennik.kategorie || []).includes(nazwa)) {
    pokazKomunikat(`Kategoria „${Produkty.escape(nazwa)}” już istnieje.`, "ostrzezenie");
    return;
  }
  cennik.kategorie = [...(cennik.kategorie || []), nazwa];
  pole.value = "";
  oznaczZmiane();
  renderKategorie();
  if (wybrany !== null) renderFormularz();
  pokazKomunikat(`Kategoria „${Produkty.escape(nazwa)}” pojawi się w filtrze sklepu po zapisie.`, "ostrzezenie");
});

qs("#lista-kategorii").addEventListener("click", (e) => {
  const nazwa = e.target.dataset?.kategoria;
  if (!nazwa) return;
  const uzywana = cennik.wina.filter((w) => w.kategoria === nazwa).length;
  if (uzywana > 0) {
    pokazKomunikat(`Nie można usunąć — kategorii „${Produkty.escape(nazwa)}” używa ${uzywana} pozycji.`, "blad");
    return;
  }
  cennik.kategorie = cennik.kategorie.filter((k) => k !== nazwa);
  oznaczZmiane();
  renderKategorie();
  if (wybrany !== null) renderFormularz();
});

// --- pomoc w opisie -------------------------------------------------------

qs("#notatki").addEventListener("input", (e) => {
  qs("#licznik-znakow").textContent = `${e.target.value.length} znaków`;
});

qs("#przygotuj").addEventListener("click", async () => {
  if (wybrany === null) {
    pokazKomunikat("Najpierw wybierz albo dodaj pozycję, dla której mam przygotować opis.", "ostrzezenie");
    return;
  }
  const tekst = qs("#notatki").value.trim();
  if (!tekst) {
    pokazKomunikat("Wklej najpierw treść, z której mam przygotować opis.", "ostrzezenie");
    return;
  }

  const wino = cennik.wina[wybrany];
  const przycisk = qs("#przygotuj");
  przycisk.disabled = true;
  przycisk.textContent = "Przygotowuję…";
  try {
    const odp = await fetch("api/opisz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tekst,
        kontekst: {
          nazwa: wino.nazwa, kategoria: wino.kategoria,
          rocznik: wino.rocznik, odmiana_slug: wino.odmiana_slug,
        },
      }),
    });
    const wynik = await odp.json();
    if (!odp.ok) {
      pokazKomunikat(Produkty.escape(wynik.komunikat || `HTTP ${odp.status}`), "blad");
      return;
    }
    // Propozycja trafia na ekran, nie do pliku — wstawia ją dopiero klikniecie.
    qs("#wynik-opis").textContent = wynik.opis;
    qs("#wynik-meta").textContent = `${wynik.opis_meta} (${wynik.opis_meta.length} znaków)`;
    qs("#wynik-meta").dataset.tresc = wynik.opis_meta;
    qs("#wyniki-opisu").hidden = false;
    ukryjKomunikat();
  } catch (blad) {
    pokazKomunikat(`Nie udało się przygotować opisu: ${blad.message}`, "blad");
  } finally {
    przycisk.disabled = false;
    przycisk.textContent = "Przygotuj opis";
  }
});

qs("#wstaw-opis").addEventListener("click", () => {
  if (wybrany === null) return;
  qs("#formularz").elements.opis.value = qs("#wynik-opis").textContent;
  zbierzFormularz();
  oznaczZmiane();
  renderPodglad();
  renderLista();
  pokazKomunikat("Opis wstawiony do formularza. Kliknij „Zapisz”, żeby go utrwalić.", "ostrzezenie");
});

qs("#kopiuj-meta").addEventListener("click", async () => {
  const tresc = qs("#wynik-meta").dataset.tresc || "";
  try {
    await navigator.clipboard.writeText(tresc);
    pokazKomunikat("Skopiowano opis meta do schowka.", "sukces");
  } catch {
    pokazKomunikat("Przeglądarka nie pozwoliła na kopiowanie — zaznacz tekst i skopiuj ręcznie.", "ostrzezenie");
  }
});

qs("#zapisz").addEventListener("click", zapisz);

qs("#odrzuc").addEventListener("click", async () => {
  wybrany = null;
  qs("#sekcja-formularza").hidden = true;
  oznaczZmiane(false);
  ukryjKomunikat();
  await wczytaj();
});

window.addEventListener("beforeunload", (e) => {
  if (!zmienione) return;
  e.preventDefault();
  e.returnValue = "";
});

wczytaj();
