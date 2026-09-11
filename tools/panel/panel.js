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
// Niezmutowana migawka cennika z ostatniego wczytania/udanego zapisu — do wykrycia
// konfliktu (patrz zapisz()). `cennik` jest mutowany w miejscu przy kazdej edycji,
// wiec bez osobnej kopii nie ma z czym porownac "co bylo, zanim ktos inny zapisal".
let cennikBazowy = null;
let wersjaCennika = null;
let zdjecia = [];
let odmiany = [];
let wybrany = null; // indeks edytowanej pozycji
let zmienione = false;
let galeriaStan = { katalogi: [], pliki: [] };
let galeriaKatalog = "";
let galeriaZaznaczone = new Set();

// Wydarzenia to drugi, niezalezny plik danych — wlasny stan i wlasny zapis.
let wydarzenia = [];
let wydarzeniaBazowe = null; // migawka jak cennikBazowy, patrz komentarz wyzej
let wersjaWydarzen = null;
let wybraneWydarzenie = null; // indeks edytowanego wpisu
let zmienioneWydarzenia = false;

// Galeria dla zdarzeń — niezalezny stan
let galeriaWydarzeniaStan = { katalogi: [], pliki: [] };
let galeriaWydarzeniaStan_katalog = "";
let galeriaWydarzeniaStan_zaznaczone = new Set();
let galeriaWydarzeniaStan_strona = 0;
const GALERIA_Wydarzenia_NA_STRONE = 16;

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

/** Jeden wskaznik na caly panel: przyciski zapisu naleza do sekcji, ale ostrzezenie
 *  „masz niezapisana prace" ma byc widoczne niezaleznie od tego, ktora sekcje widac. */
function odswiezWskaznikZmian() {
  const cos = zmienione || zmienioneWydarzenia;
  qs("#stan-zmian").textContent = cos ? "● niezapisane zmiany" : "";
}

function oznaczZmiane(stan = true) {
  zmienione = stan;
  odswiezWskaznikZmian();
}

function oznaczZmianeWydarzen(stan = true) {
  zmienioneWydarzenia = stan;
  odswiezWskaznikZmian();
}

// --- wczytanie ------------------------------------------------------------

async function wczytaj() {
  try {
    const odp = await fetch("api/wczytaj");
    const dane = await odp.json();
    if (!odp.ok) throw new Error(dane.komunikat || `HTTP ${odp.status}`);
    cennik = dane.cennik;
    cennikBazowy = JSON.parse(JSON.stringify(cennik));
    wersjaCennika = dane.wersja;
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
          <span class="meta id">${Produkty.escape(wino.id || "—")}</span>
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

function renderRodzaje() {
  qs("#lista-rodzajow").innerHTML = (cennik.rodzaje || [])
    .map(
      (nazwa) => `<li>${Produkty.escape(nazwa)}
        <button type="button" data-rodzaj="${Produkty.escape(nazwa)}" title="Usuń">×</button></li>`
    )
    .join("");
}

function renderWszystko() {
  renderLista();
  renderKategorie();
  renderRodzaje();
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
  f.elements.rodzaj.innerHTML = opcje(cennik.rodzaje || [], wino.rodzaj);
  f.elements.zdjecie.innerHTML = opcje(zdjecia, wino.zdjecie);

  ["nazwa", "id", "opis", ...POLA_LICZBOWE].forEach((pole) => {
    const wartosc = wino[pole];
    f.elements[pole].value = wartosc === undefined || wartosc === null ? "" : wartosc;
  });
  f.elements.zdjecie_sklep.value = wino.zdjecie_sklep || "";
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
  const rodzaj = f.elements.rodzaj.value.trim();
  if (rodzaj) wino.rodzaj = rodzaj;
  else delete wino.rodzaj;
  const zdjecieSklep = f.elements.zdjecie_sklep.value.trim();
  if (zdjecieSklep) wino.zdjecie_sklep = zdjecieSklep;
  else delete wino.zdjecie_sklep;
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
  if (wino.rodzaj && !(cennik.rodzaje || []).includes(wino.rodzaj))
    dodaj("rodzaj", "Nieznany rodzaj");
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
      body: JSON.stringify({ wersja: wersjaCennika, bazowe_dane: cennikBazowy, dane: cennik }),
    });
    const wynik = await odp.json();
    if (!odp.ok) {
      if (wynik.konflikt) {
        // Ktos inny zapisal ten plik pomiedzy naszym wczytaniem a naszym zapisem —
        // zapis serwera odrzucil, dysk nie zostal dotkniety (patrz cennik.zapisz_bezpiecznie).
        const roznice = Array.isArray(wynik.roznice) ? wynik.roznice : [];
        const lista = roznice.length
          ? `<ul>${roznice.map((r) => `<li>${Produkty.escape(r)}</li>`).join("")}</ul>`
          : "";
        pokazKomunikat(
          `${Produkty.escape(wynik.komunikat)}${lista}<br>` +
            `Kliknij „Odrzuć zmiany”, żeby wczytać najnowszą wersję, a potem wprowadź ` +
            `swoją zmianę ponownie.`,
          "ostrzezenie"
        );
        return;
      }
      // Walidacja odsyla `bledy`, awaria zapisu — `komunikat`. Bez tej drugiej galezi
      // blad uprawnien do pliku pokazywal sie jako pusta lista.
      const lista = (wynik.bledy || [])
        .map((b) => `<li>${b.pozycja === null ? "cały plik" : `pozycja ${b.pozycja + 1}`}: ${Produkty.escape(b.komunikat)}</li>`)
        .join("");
      const tresc = lista
        ? `Serwer odrzucił zapis:<ul>${lista}</ul>`
        : `Nie udało się zapisać (HTTP ${odp.status}): ${Produkty.escape(wynik.komunikat || "serwer nie podał powodu")}`;
      pokazKomunikat(tresc, "blad");
      return;
    }
    oznaczZmiane(false);
    wersjaCennika = wynik.wersja;
    cennikBazowy = JSON.parse(JSON.stringify(cennik));
    // Na produkcji cennik zyje poza katalogiem wdrozenia, wiec zmiana dziala od razu
    // i nie wymaga commita. Lokalnie zapisuje sie plik z repozytorium.
    const lokalnie = ["localhost", "127.0.0.1"].includes(location.hostname);
    const skutek = lokalnie
      ? "Zmiana jest na razie tylko na Twoim dysku — żeby trafiła na stronę, zrób commit i wdrożenie."
      : "Zmiana jest już widoczna na stronie. Kopia w repozytorium się nie zmienia — to wersja startowa.";
    pokazKomunikat(
      `✓ Zapisano ${wynik.pozycji} pozycji.<br>${skutek}<br>` +
        `<span class="podpowiedz">Poprzednia wersja: <code>${Produkty.escape(wynik.kopia)}</code></span>`,
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

qs("#dodaj-rodzaj").addEventListener("click", () => {
  const pole = qs("#nowy-rodzaj");
  const nazwa = pole.value.trim();
  if (!nazwa) return;
  if ((cennik.rodzaje || []).includes(nazwa)) {
    pokazKomunikat(`Rodzaj „${Produkty.escape(nazwa)}” już istnieje.`, "ostrzezenie");
    return;
  }
  cennik.rodzaje = [...(cennik.rodzaje || []), nazwa];
  pole.value = "";
  oznaczZmiane();
  renderRodzaje();
  if (wybrany !== null) renderFormularz();
  pokazKomunikat(`Rodzaj „${Produkty.escape(nazwa)}” pojawi się w formularzu pozycji po zapisie.`, "ostrzezenie");
});

// --- konfiguracja poczty (SMTP) ---------------------------------------------
// Dane logowania nie wracaja z serwera nigdy — tylko status "skonfigurowano/brak".
// Kazdy zapis nadpisuje poprzednie dane w calosci (patrz kontakt.zapisz_smtp_dane).

async function wczytajStatusSmtp() {
  const status = qs("#smtp-status");
  try {
    const odp = await fetch("api/smtp-wczytaj");
    const dane = await odp.json();
    status.textContent = dane.skonfigurowano ? "skonfigurowano ✓" : "brak danych logowania";
  } catch (_) {
    status.textContent = "nie udało się sprawdzić";
  }
}

qs("#zapisz-smtp").addEventListener("click", async () => {
  const formularz = qs("#formularz-smtp");
  const user = formularz.elements.smtp_user.value.trim();
  const password = formularz.elements.smtp_password.value;
  if (!user || !password) {
    pokazKomunikat("Podaj adres e-mail i hasło aplikacji przed zapisem.", "blad");
    return;
  }
  const przycisk = qs("#zapisz-smtp");
  przycisk.disabled = true;
  try {
    const odp = await fetch("api/smtp-zapisz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user, password }),
    });
    const wynik = await odp.json();
    if (!odp.ok || !wynik.ok) {
      pokazKomunikat(
        `Nie udało się zapisać danych logowania: ${Produkty.escape(wynik.komunikat || "serwer nie podał powodu")}`,
        "blad"
      );
      return;
    }
    formularz.reset();
    await wczytajStatusSmtp();
    pokazKomunikat("✓ Zapisano dane logowania SMTP.", "sukces");
  } catch (blad) {
    pokazKomunikat(`Nie udało się zapisać danych logowania: ${Produkty.escape(blad.message)}`, "blad");
  } finally {
    przycisk.disabled = false;
  }
});

qs("#lista-rodzajow").addEventListener("click", (e) => {
  const nazwa = e.target.dataset?.rodzaj;
  if (!nazwa) return;
  const uzywany = cennik.wina.filter((w) => w.rodzaj === nazwa).length;
  if (uzywany > 0) {
    pokazKomunikat(`Nie można usunąć — rodzaju „${Produkty.escape(nazwa)}” używa ${uzywany} pozycji.`, "blad");
    return;
  }
  cennik.rodzaje = cennik.rodzaje.filter((r) => r !== nazwa);
  oznaczZmiane();
  renderRodzaje();
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


// --- galeria -------------------------------------------------------------

function nazwaKatalogu(sciezka) {
  return sciezka ? `attached_assets/${sciezka}` : "attached_assets (główny)";
}

function adresZasobu(sciezka) {
  return `../../attached_assets/${sciezka.split("/").map(encodeURIComponent).join("/")}`;
}

function rozmiarPliku(bajty) {
  if (bajty < 1024) return `${bajty} B`;
  if (bajty < 1024 * 1024) return `${(bajty / 1024).toFixed(0)} KB`;
  return `${(bajty / (1024 * 1024)).toFixed(1)} MB`;
}

function wariantPliku(nazwa) {
  const wynik = nazwa.match(/-(sm|thumb)\.[^.]+$/i);
  return wynik ? `-${wynik[1]}` : "";
}

function ustawOpcjeKatalogow() {
  const katalogi = galeriaStan.katalogi || [];
  const filtr = qs("#galeria-katalog");
  const cel = qs("#galeria-cel");
  const poprzedniCel = cel.value;
  filtr.innerHTML = `<option value="">Wszystkie katalogi</option>` +
    katalogi.map((katalog) => `<option value="${Produkty.escape(katalog)}">${Produkty.escape(nazwaKatalogu(katalog))}</option>`).join("");
  cel.innerHTML = katalogi
    .map((katalog) => `<option value="${Produkty.escape(katalog)}">${Produkty.escape(nazwaKatalogu(katalog))}</option>`)
    .join("");
  filtr.value = galeriaKatalog;
  cel.value = katalogi.includes(poprzedniCel) ? poprzedniCel : "";
}

function odswiezAkcjeGalerii(liczba) {
  qs("#galeria-zaznaczenie").textContent = liczba
    ? `Zaznaczono: ${liczba}`
    : "Zaznacz obrazy, aby je przenieść albo utworzyć warianty.";
  qs("#przenies-zdjecia").disabled = liczba === 0;
  qs("#utworz-warianty").disabled = liczba === 0;
}

function renderGaleria() {
  ustawOpcjeKatalogow();
  const widoczne = galeriaStan.pliki.filter((plik) =>
    !galeriaKatalog || plik.katalog === galeriaKatalog
  );
  const grid = qs("#galeria-grid");
  qs("#licznik-galerii").textContent = `(${widoczne.length} obrazów)`;
  qs("#galeria-pusto").hidden = widoczne.length > 0;
  grid.innerHTML = widoczne.map((plik) => {
    const wybranyPlik = galeriaZaznaczone.has(plik.sciezka);
    const wymiary = plik.szerokosc && plik.wysokosc
      ? `${plik.szerokosc} × ${plik.wysokosc} px`
      : "wymiary niedostępne";
    const wariant = wariantPliku(plik.nazwa);
    return `
      <article class="galeria-karta${wybranyPlik ? " wybrana" : ""}">
        <input class="galeria-zaznacz" type="checkbox" data-galeria-zaznacz="${Produkty.escape(plik.sciezka)}"
          aria-label="Zaznacz ${Produkty.escape(plik.nazwa)}"${wybranyPlik ? " checked" : ""}>
        <button type="button" class="galeria-obraz" data-galeria-podglad="${Produkty.escape(plik.sciezka)}">
          <img src="${adresZasobu(plik.sciezka)}" alt="${Produkty.escape(plik.nazwa)}" loading="lazy">
        </button>
        <div class="galeria-dane">
          <p class="galeria-nazwa">${Produkty.escape(plik.nazwa)}</p>
          <p class="galeria-meta">${Produkty.escape(nazwaKatalogu(plik.katalog))}</p>
          <p class="galeria-meta">${wymiary} · ${rozmiarPliku(plik.rozmiar)}${wariant ? ` · <span class="galeria-wariant">${wariant}</span>` : ""}</p>
          <button type="button" class="przycisk galeria-uzyj" data-galeria-uzyj="${Produkty.escape(plik.sciezka)}">Użyj jako zdjęcia produktu w sklepie</button>
        </div>
      </article>`;
  }).join("");
  odswiezAkcjeGalerii(galeriaZaznaczone.size);
}

async function wczytajGalerie() {
  try {
    const odp = await fetch("api/galeria-wczytaj");
    const dane = await odp.json();
    if (!odp.ok) throw new Error(dane.komunikat || `HTTP ${odp.status}`);
    galeriaStan = {
      katalogi: Array.isArray(dane.katalogi) ? dane.katalogi : [],
      pliki: Array.isArray(dane.pliki) ? dane.pliki : [],
    };
    // Także dla galerii w formularzu zadarzeń
    galeriaWydarzeniaStan = {
      katalogi: galeriaStan.katalogi,
      pliki: galeriaStan.pliki,
    };
    const istniejace = new Set(galeriaStan.pliki.map((plik) => plik.sciezka));
    galeriaZaznaczone = new Set([...galeriaZaznaczone].filter((plik) => istniejace.has(plik)));
    renderGaleria();
  } catch (blad) {
    pokazKomunikat(`Nie udało się wczytać galerii: ${Produkty.escape(blad.message)}`, "blad");
  }
}

function pokazPodgladGalerii(sciezka) {
  const plik = galeriaStan.pliki.find((wpis) => wpis.sciezka === sciezka);
  if (!plik) return;
  qs("#galeria-modal-tytul").textContent = plik.nazwa;
  qs("#galeria-modal-obraz").src = adresZasobu(plik.sciezka);
  qs("#galeria-modal-obraz").alt = plik.nazwa;
  qs("#galeria-modal-opis").textContent = `${nazwaKatalogu(plik.katalog)} · ${rozmiarPliku(plik.rozmiar)}`;
  qs("#galeria-modal").hidden = false;
  qs("#zamknij-galerie").focus();
}

function uzyjZdjeciaGalerii(sciezka) {
  if (wybrany === null) {
    pokazKomunikat("Najpierw wybierz produkt w sekcji „Pozycje”.", "ostrzezenie");
    return;
  }
  const plik = galeriaStan.pliki.find((wpis) => wpis.sciezka === sciezka);
  if (!plik) return;
  const wino = cennik.wina[wybrany];
  wino.zdjecie_sklep = plik.sciezka;
  qs("#formularz").elements.zdjecie_sklep.value = plik.sciezka;
  zbierzFormularz();
  oznaczZmiane();
  renderPodglad();
  pokazKomunikat(`Podpięto „${Produkty.escape(plik.nazwa)}” do produktu „${Produkty.escape(wino.nazwa)}”. Kliknij „Zapisz”, aby utrwalić zmianę.`, "ostrzezenie");
}

function zamknijPodgladGalerii() {
  qs("#galeria-modal").hidden = true;
  qs("#galeria-modal-obraz").removeAttribute("src");
}

function wybranePlikiGalerii() {
  return [...galeriaZaznaczone];
}

async function przeniesZaznaczone() {
  const pliki = wybranePlikiGalerii();
  if (!pliki.length) return;
  const przycisk = qs("#przenies-zdjecia");
  przycisk.disabled = true;
  try {
    const odp = await fetch("api/galeria-przenies", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pliki, katalog: qs("#galeria-cel").value }),
    });
    const wynik = await odp.json();
    if (!odp.ok) throw new Error(wynik.komunikat || `HTTP ${odp.status}`);
    galeriaZaznaczone.clear();
    await wczytajGalerie();
    pokazKomunikat(`✓ Przeniesiono ${wynik.przeniesiono} obrazów. Zmiana jest zapisana na dysku.`, "sukces");
  } catch (blad) {
    pokazKomunikat(`Nie udało się przenieść obrazów: ${Produkty.escape(blad.message)}`, "blad");
  } finally {
    przycisk.disabled = false;
  }
}

async function utworzWarianty() {
  const warianty = [];
  if (qs("#wariant-sm").checked) warianty.push("sm");
  if (qs("#wariant-thumb").checked) warianty.push("thumb");
  const pliki = wybranePlikiGalerii();
  if (!pliki.length) return;
  if (!warianty.length) {
    pokazKomunikat("Wybierz co najmniej jeden wariant: -sm albo -thumb.", "ostrzezenie");
    return;
  }
  const przycisk = qs("#utworz-warianty");
  przycisk.disabled = true;
  try {
    const odp = await fetch("api/galeria-warianty", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pliki, warianty }),
    });
    const wynik = await odp.json();
    if (!odp.ok) throw new Error(wynik.komunikat || `HTTP ${odp.status}`);
    galeriaZaznaczone.clear();
    await wczytajGalerie();
    const pominieto = wynik.pominieto ? ` Pominięto istniejących: ${wynik.pominieto}.` : "";
    pokazKomunikat(`✓ Utworzono wariantów: ${wynik.utworzono}.${pominieto}`, "sukces");
  } catch (blad) {
    pokazKomunikat(`Nie udało się utworzyć wariantów: ${Produkty.escape(blad.message)}`, "blad");
  } finally {
    przycisk.disabled = false;
  }
}

qs("#galeria-katalog").addEventListener("change", (e) => {
  galeriaKatalog = e.target.value;
  renderGaleria();
});

qs("#galeria-grid").addEventListener("change", (e) => {
  const checkbox = e.target.closest("[data-galeria-zaznacz]");
  if (!checkbox) return;
  const sciezka = checkbox.dataset.galeriaZaznacz;
  if (checkbox.checked) galeriaZaznaczone.add(sciezka);
  else galeriaZaznaczone.delete(sciezka);
  renderGaleria();
});

qs("#galeria-grid").addEventListener("click", (e) => {
  const uzyj = e.target.closest("[data-galeria-uzyj]");
  if (uzyj) {
    e.preventDefault();
    uzyjZdjeciaGalerii(uzyj.dataset.galeriaUzyj);
    return;
  }
  const podglad = e.target.closest("[data-galeria-podglad]");
  if (podglad) pokazPodgladGalerii(podglad.dataset.galeriaPodglad);
});
qs("#odswiez-galerie").addEventListener("click", wczytajGalerie);
qs("#przenies-zdjecia").addEventListener("click", przeniesZaznaczone);
qs("#utworz-warianty").addEventListener("click", utworzWarianty);
qs("#wyczysc-zdjecie-sklep").addEventListener("click", () => {
  if (wybrany === null) return;
  qs("#formularz").elements.zdjecie_sklep.value = "";
  zbierzFormularz();
  oznaczZmiane();
  renderPodglad();
  pokazKomunikat("Usunięto zdjęcie produktu w sklepie z formularza. Kliknij „Zapisz”, aby utrwalić zmianę.", "ostrzezenie");
});
qs("#zamknij-galerie").addEventListener("click", zamknijPodgladGalerii);
qs("#galeria-modal").addEventListener("click", (e) => {
  if (e.target.closest("[data-galeria-zamknij]")) zamknijPodgladGalerii();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !qs("#galeria-modal").hidden) zamknijPodgladGalerii();
});


// --- wydarzenia -----------------------------------------------------------
const POLA_WYDARZENIA = ["tytul", "tresc", "data_od", "data_do", "data_publikacji_od", "zdjecie"];
const POLA_OPCJONALNE_WYDARZENIA = ["data_publikacji_od", "zdjecie"];

// Drugi plik danych, wlasna walidacja po stronie serwera, wlasny zapis. Panel widzi
// WSZYSTKIE wpisy — take nieaktywne; o tym, co zobaczy odwiedzajacy, decyduje serwer
// (wydarzenia.aktywne w Pythonie). Znacznik stanu ponizej jest tylko informacja.

/** Dzisiejsza data w strefie winnicy jako "RRRR-MM-DD". Locale sv-SE daje wlasnie ten format. */
function dzisWWinnicy() {
  return new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Warsaw" }).format(new Date());
}

/** Cztery stany, bo od kiedy wpis jest WIDOCZNY, a od kiedy wydarzenie TRWA, to dwie
 *  rozne daty. Szary = nie ma go na stronie, bursztyn = widoczny jako zapowiedz,
 *  zielony = trwa wlasnie teraz. */
function stanWydarzenia(wpis) {
  const dzis = dzisWWinnicy();
  if (!wpis.data_od || !wpis.data_do) return { klasa: "stan-zakonczone", opis: "brak dat" };
  const poczatek = wpis.data_publikacji_od || wpis.data_od;
  if (dzis > wpis.data_do) return { klasa: "stan-zakonczone", opis: "zakończone" };
  if (dzis < poczatek) return { klasa: "stan-zakonczone", opis: "ukryte" };
  if (dzis < wpis.data_od) return { klasa: "stan-przyszle", opis: "zapowiedź" };
  return { klasa: "stan-aktywne", opis: "aktywne" };
}

function renderFormularzWydarzenia() {
  const wpis = wydarzenia[wybraneWydarzenie];
  const sekcja = qs("#sekcja-formularza-wydarzenia");
  if (!wpis) {
    sekcja.hidden = true;
    return;
  }
  sekcja.hidden = false;
  qs("#tytul-formularza-wydarzenia").textContent = wpis.tytul || "Wydarzenie";
  const formularz = qs("#formularz-wydarzenia");
  formularz.elements.zdjecie.innerHTML = opcje(zdjecia, wpis.zdjecie);
  POLA_WYDARZENIA.forEach((pole) => {
    formularz.elements[pole].value = wpis[pole] || "";
  });
  // Ustaw radio wyswietl_w
  const wyswietl_w = wpis.wyswietl_w || "wydarzenia";
  qsa("input[name='wyswietl_w']").forEach(r => r.checked = (r.value === wyswietl_w));
  // Pokaż/ukryj galerię i listę zdjęć
  if (wpis.zdjecia && wpis.zdjecia.length > 0) {
    qs("#zdjecia-wydarzenia").hidden = false;
    renderZdjeciaWydarzenia();
  } else {
    qs("#zdjecia-wydarzenia").hidden = true;
  }
  // Przygotuj galerię (ustal katalogi)
  ustawOpcjeKataloguWydarzenia();
  renderGaleriaWydarzenia();
}

function ustawOpcjeKataloguWydarzenia() {
  const katalogi = galeriaWydarzeniaStan.katalogi || [];
  const filtr = qs("#galeria-wydarzenia-katalog");
  const poprzedniKatalog = galeriaWydarzeniaStan_katalog;
  filtr.innerHTML = `<option value="">Wszystkie katalogi</option>` +
    katalogi.map((katalog) => `<option value="${Produkty.escape(katalog)}">${Produkty.escape(nazwaKatalogu(katalog))}</option>`).join("");
  filtr.value = galeriaWydarzeniaStan_katalog;
}

function renderGaleriaWydarzenia() {
  const widoczne = galeriaWydarzeniaStan.pliki.filter((plik) =>
    !galeriaWydarzeniaStan_katalog || plik.katalog === galeriaWydarzeniaStan_katalog
  );
  const stronaStart = galeriaWydarzeniaStan_strona * GALERIA_Wydarzenia_NA_STRONE;
  const stronaKoniec = stronaStart + GALERIA_Wydarzenia_NA_STRONE;
  const naStrone = widoczne.slice(stronaStart, stronaKoniec);

  const grid = qs("#galeria-wydarzenia-grid");
  grid.innerHTML = naStrone.map((plik) => {
    const wybranyPlik = galeriaWydarzeniaStan_zaznaczone.has(plik.sciezka);
    const wymiary = plik.szerokosc && plik.wysokosc
      ? `${plik.szerokosc} × ${plik.wysokosc} px`
      : "wymiary niedostępne";
    return `
      <article class="galeria-karta${wybranyPlik ? " wybrana" : ""}">
        <input class="galeria-zaznacz" type="checkbox" data-galeria-wydarzenie="${Produkty.escape(plik.sciezka)}"
          aria-label="Zaznacz ${Produkty.escape(plik.nazwa)}"${wybranyPlik ? " checked" : ""}>
        <button type="button" class="galeria-obraz" data-galeria-podglad-wyd="${Produkty.escape(plik.sciezka)}">
          <img src="${adresZasobu(plik.sciezka)}" alt="${Produkty.escape(plik.nazwa)}" loading="lazy">
        </button>
        <div class="galeria-dane">
          <p class="galeria-nazwa">${Produkty.escape(plik.nazwa)}</p>
          <p class="galeria-meta">${wymiary}</p>
        </div>
      </article>`;
  }).join("");

  renderPaginacjaWydarzenia(widoczne.length);
  odswiezAkcjeGaleriiWydarzenia(galeriaWydarzeniaStan_zaznaczone.size);
}

function renderPaginacjaWydarzenia(wszystko) {
  const liczbStron = Math.ceil(wszystko / GALERIA_Wydarzenia_NA_STRONE);
  const paginacja = qs("#galeria-wydarzenia-paginacja");
  if (liczbStron <= 1) {
    paginacja.innerHTML = "";
    return;
  }
  let html = "";
  for (let i = 0; i < liczbStron; i++) {
    const aktywna = i === galeriaWydarzeniaStan_strona ? " style=\"font-weight: 600; color: var(--akcent);\"" : "";
    html += `<button type="button" data-strona="${i}" class="przycisk" ${aktywna} style="padding: 0.4rem 0.6rem; font-size: 0.85rem;">${i + 1}</button>`;
  }
  paginacja.innerHTML = html;
}

function renderZdjeciaWydarzenia() {
  if (wybraneWydarzenie === null) return;
  const wpis = wydarzenia[wybraneWydarzenie];
  const lista = qs("#lista-zdjecialb-wydarzenia");
  lista.innerHTML = (wpis.zdjecia || []).map((zdjecie, i) => `
    <li data-indeks="${i}" style="padding: 0.5rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem;">
      <span>${Produkty.escape(zdjecie)}</span>
      <button type="button" class="przycisk" data-usun-zdjecie="${i}" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Usuń</button>
    </li>`).join("");
}

function odswiezAkcjeGaleriiWydarzenia(liczba) {
  qs("#galeria-wydarzenia-zaznaczenie").textContent = liczba
    ? `Zaznaczono: ${liczba}`
    : "Zaznacz obrazy, aby je dodać do tego Wydarzenia.";
  qs("#dodaj-zdjecia-do-wydarzenia").style.display = liczba > 0 ? "block" : "none";
}

async function wczytajWydarzenia() {
  try {
    const odp = await fetch("api/wydarzenia-wczytaj");
    const dane = await odp.json();
    if (!odp.ok) throw new Error(dane.komunikat || `HTTP ${odp.status}`);
    wydarzenia = Array.isArray(dane.wydarzenia) ? dane.wydarzenia : [];
    wydarzeniaBazowe = JSON.parse(JSON.stringify(wydarzenia));
    wersjaWydarzen = dane.wersja;
    qs("#sciezka-wydarzen").textContent = dane.sciezka;
    renderListeWydarzen();
  } catch (blad) {
    pokazKomunikat(`Nie udało się wczytać wydarzeń: ${Produkty.escape(blad.message)}`, "blad");
  }
}

function renderListeWydarzen() {
  const lista = qs("#lista-wydarzen-panel");
  qs("#licznik-wydarzen").textContent = wydarzenia.length ? `(${wydarzenia.length})` : "";
  qs("#pusto-wydarzenia").hidden = wydarzenia.length > 0;

  lista.innerHTML = wydarzenia
    .map((wpis, i) => {
      const stan = stanWydarzenia(wpis);
      const okres = wpis.data_od === wpis.data_do
        ? Produkty.escape(wpis.data_od || "—")
        : `${Produkty.escape(wpis.data_od || "—")} – ${Produkty.escape(wpis.data_do || "—")}`;
      return `
        <li data-wydarzenie="${i}" class="${i === wybraneWydarzenie ? "wybrana" : ""}">
          <span class="nazwa">${Produkty.escape(wpis.tytul || "(bez tytułu)")}</span>
          <span class="meta okres">${okres}</span>
          <span class="znacznik-stanu ${stan.klasa}">${stan.opis}</span>
        </li>`;
    })
    .join("");
}

function wybierzWydarzenie(indeks) {
  wybraneWydarzenie = indeks;
  renderListeWydarzen();
  renderFormularzWydarzenia();
}

function zbierzFormularzWydarzenia() {
  if (wybraneWydarzenie === null) return;
  const formularz = qs("#formularz-wydarzenia");
  const wpis = wydarzenia[wybraneWydarzenie];
  POLA_WYDARZENIA.forEach((pole) => {
    wpis[pole] = formularz.elements[pole].value;
  });
  // Puste pola opcjonalne usuwamy zamiast zapisywac "" — walidator traktuje brak klucza
  // i pusty napis tak samo, ale plik danych zostaje bez smieci.
  POLA_OPCJONALNE_WYDARZENIA.forEach((pole) => {
    if (!wpis[pole]) delete wpis[pole];
  });
  // Ustaw wyswietl_w z wybranego radio
  const wyswietl_w = qs("input[name='wyswietl_w']:checked")?.value || "wydarzenia";
  wpis.wyswietl_w = wyswietl_w;
  // Identyfikator nie jest polem formularza — wynika z tytulu i musi zostac unikalny,
  // bo to on rozroznia wpisy przy zapisie.
  wpis.id = unikalneIdWydarzenia(wpis.tytul, wybraneWydarzenie);
  qs("#tytul-formularza-wydarzenia").textContent = wpis.tytul || "Wydarzenie";
}

/** Sam slug, bez deduplikacji — proponujId() jest cennikowe: siega do cennik.wina
 *  i do `wybrany`, a wydarzenia moga wczytac sie zanim cennik w ogole dojdzie. */
function slugWydarzenia(tytul) {
  return (tytul || "")
    .toLowerCase()
    .replace(/[ąćęłńóśźż]/g, (z) => ZNAKI[z])
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function unikalneIdWydarzenia(tytul, pomijanyIndeks) {
  const podstawa = slugWydarzenia(tytul) || "wydarzenie";
  const zajete = new Set(
    wydarzenia.filter((_, i) => i !== pomijanyIndeks).map((w) => w.id)
  );
  if (!zajete.has(podstawa)) return podstawa;
  let n = 2;
  while (zajete.has(`${podstawa}-${n}`)) n += 1;
  return `${podstawa}-${n}`;
}

async function zapiszWydarzenia() {
  qs("#zapisz-wydarzenia").disabled = true;
  try {
    const odp = await fetch("api/wydarzenia-zapisz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        wersja: wersjaWydarzen,
        bazowe_dane: { wydarzenia: wydarzeniaBazowe },
        dane: { wydarzenia },
      }),
    });
    const wynik = await odp.json();
    if (!odp.ok) {
      if (wynik.konflikt) {
        const roznice = Array.isArray(wynik.roznice) ? wynik.roznice : [];
        const lista = roznice.length
          ? `<ul>${roznice.map((r) => `<li>${Produkty.escape(r)}</li>`).join("")}</ul>`
          : "";
        pokazKomunikat(
          `${Produkty.escape(wynik.komunikat)}${lista}<br>` +
            `Kliknij „Odrzuć zmiany”, żeby wczytać najnowszą wersję, a potem wprowadź ` +
            `swoją zmianę ponownie.`,
          "ostrzezenie"
        );
        return;
      }
      const lista = (wynik.bledy || [])
        .map((b) => `<li>${b.pozycja === null ? "cały plik" : `wydarzenie ${b.pozycja + 1}`}: ` +
                    `${Produkty.escape(b.komunikat)}${b.pole ? ` (${Produkty.escape(b.pole)})` : ""}</li>`)
        .join("");
      const tresc = lista
        ? `Serwer odrzucił zapis wydarzeń:<ul>${lista}</ul>`
        : `Nie udało się zapisać wydarzeń (HTTP ${odp.status}): ` +
          `${Produkty.escape(wynik.komunikat || "serwer nie podał powodu")}`;
      pokazKomunikat(tresc, "blad");
      return;
    }
    oznaczZmianeWydarzen(false);
    wersjaWydarzen = wynik.wersja;
    wydarzeniaBazowe = JSON.parse(JSON.stringify(wydarzenia));
    const lokalnie = ["localhost", "127.0.0.1"].includes(location.hostname);
    const skutek = lokalnie
      ? "Zmiana jest na razie tylko na Twoim dysku — żeby trafiła na stronę, zrób commit i wdrożenie."
      : "Zmiana jest już widoczna na stronie.";
    pokazKomunikat(
      `✓ Zapisano ${wynik.pozycji} wydarzeń.<br>${skutek}<br>` +
        `<span class="podpowiedz">Poprzednia wersja: <code>${Produkty.escape(wynik.kopia)}</code></span>`,
      "sukces"
    );
  } catch (blad) {
    pokazKomunikat(`Nie udało się zapisać wydarzeń: ${Produkty.escape(blad.message)}`, "blad");
  } finally {
    qs("#zapisz-wydarzenia").disabled = false;
  }
}

qs("#lista-wydarzen-panel").addEventListener("click", (e) => {
  const wiersz = e.target.closest("li[data-wydarzenie]");
  if (wiersz) wybierzWydarzenie(Number(wiersz.dataset.wydarzenie));
});

qs("#formularz-wydarzenia").addEventListener("input", () => {
  zbierzFormularzWydarzenia();
  oznaczZmianeWydarzen();
  renderListeWydarzen();
});

qs("#dodaj-wydarzenie").addEventListener("click", () => {
  const dzis = dzisWWinnicy();
  wydarzenia.push({ id: "", tytul: "", tresc: "", data_od: dzis, data_do: dzis });
  wybraneWydarzenie = wydarzenia.length - 1;
  wydarzenia[wybraneWydarzenie].id = unikalneIdWydarzenia("", wybraneWydarzenie);
  oznaczZmianeWydarzen();
  renderListeWydarzen();
  renderFormularzWydarzenia();
  qs("#formularz-wydarzenia").elements.tytul.focus();
});

qs("#usun-wydarzenie").addEventListener("click", () => {
  if (wybraneWydarzenie === null) return;
  wydarzenia.splice(wybraneWydarzenie, 1);
  wybraneWydarzenie = null;
  oznaczZmianeWydarzen();
  renderListeWydarzen();
  renderFormularzWydarzenia();
});

qs("#zapisz-wydarzenia").addEventListener("click", zapiszWydarzenia);

qs("#odrzuc-wydarzenia").addEventListener("click", async () => {
  wybraneWydarzenie = null;
  qs("#sekcja-formularza-wydarzenia").hidden = true;
  oznaczZmianeWydarzen(false);
  ukryjKomunikat();
  await wczytajWydarzenia();
});

// --- galeria dla wydarzeń ---

qs("#galeria-wydarzenia-katalog").addEventListener("change", (e) => {
  galeriaWydarzeniaStan_katalog = e.target.value;
  galeriaWydarzeniaStan_strona = 0;
  renderGaleriaWydarzenia();
});

qs("#galeria-wydarzenia-grid").addEventListener("change", (e) => {
  const checkbox = e.target.closest("[data-galeria-wydarzenie]");
  if (!checkbox) return;
  const sciezka = checkbox.dataset.galeriaWydarzenie;
  if (checkbox.checked) galeriaWydarzeniaStan_zaznaczone.add(sciezka);
  else galeriaWydarzeniaStan_zaznaczone.delete(sciezka);
  renderGaleriaWydarzenia();
});

qs("#galeria-wydarzenia-paginacja").addEventListener("click", (e) => {
  const strona = e.target.dataset.strona;
  if (strona !== undefined) {
    galeriaWydarzeniaStan_strona = Number(strona);
    renderGaleriaWydarzenia();
  }
});

qs("#dodaj-zdjecia-do-wydarzenia").addEventListener("click", () => {
  if (wybraneWydarzenie === null) return;
  const wpis = wydarzenia[wybraneWydarzenie];
  if (!wpis.zdjecia) wpis.zdjecia = [];
  galeriaWydarzeniaStan_zaznaczone.forEach(sciezka => {
    if (!wpis.zdjecia.includes(sciezka)) wpis.zdjecia.push(sciezka);
  });
  galeriaWydarzeniaStan_zaznaczone.clear();
  oznaczZmianeWydarzen();
  qs("#zdjecia-wydarzenia").hidden = false;
  renderZdjeciaWydarzenia();
  renderGaleriaWydarzenia();
  pokazKomunikat(`✓ Dodano ${wpis.zdjecia.length} zdjęć do tego Wydarzenia.`, "sukces");
});

qs("#lista-zdjecialb-wydarzenia").addEventListener("click", (e) => {
  const usun = e.target.closest("[data-usun-zdjecie]");
  if (!usun) return;
  if (wybraneWydarzenie === null) return;
  const indeks = Number(usun.dataset.usunZdjecie);
  const wpis = wydarzenia[wybraneWydarzenie];
  if (wpis.zdjecia) {
    wpis.zdjecia.splice(indeks, 1);
    if (wpis.zdjecia.length === 0) {
      qs("#zdjecia-wydarzenia").hidden = true;
      delete wpis.zdjecia;
    }
    oznaczZmianeWydarzen();
    renderZdjeciaWydarzenia();
  }
});

// --- zwijanie sekcji ------------------------------------------------------
// Stan nie jest zapamietywany: po odswiezeniu wszystko jest rozwiniete. Zwijanie ma
// skracac przewijanie w trakcie pracy, a nie konfigurowac panel na stale.

function initZwijanieSekcji() {
  qsa(".przelacznik-sekcji").forEach((przycisk) => {
    przycisk.addEventListener("click", () => {
      const cialo = qs(`#${przycisk.getAttribute("aria-controls")}`);
      if (!cialo) return;
      const rozwiniete = przycisk.getAttribute("aria-expanded") === "true";
      przycisk.setAttribute("aria-expanded", String(!rozwiniete));
      cialo.hidden = rozwiniete;
      // Formularz pozycji jest logicznie czescia sekcji "Pozycje" — zwiniecie listy
      // chowa go razem z nia, rozwiniecie przywraca go tylko gdy cos jest wybrane.
      if (cialo.id === "cialo-pozycje") {
        qs("#sekcja-formularza").hidden = rozwiniete || wybrany === null;
      }
    });
  });
}

initZwijanieSekcji();

window.addEventListener("beforeunload", (e) => {
  if (!zmienione && !zmienioneWydarzenia) return;
  e.preventDefault();
  e.returnValue = "";
});

// Sekwencyjnie, nie rownolegle: formularz wydarzenia buduje <select> ze zdjeciami
// z listy, ktora przychodzi razem z cennikiem.
wczytaj().then(wczytajWydarzenia).then(wczytajGalerie);
wczytajStatusSmtp();
