/**
 * Biblioteka produktów — wyliczenia cen i render karty.
 *
 * Ładowana PRZED main.js. Nie rejestruje zdarzeń i nie dotyka DOM-u przy wczytaniu,
 * dzięki czemu używa jej także panel redakcyjny (tools/panel/) do podglądu karty.
 * Patrz .ai/GUARDRAILS.md → "Front-end bez frameworka i bez modułów, w dwóch plikach".
 */
const Produkty = {
  // Domyslne sciezki dzialaja dla strony w korzeniu. Strony w podkatalogach
  // (wina/*.html) i panel przekazuja wlasne przez `opcje` — patrz KORZEN w main.js.
  BAZA_ZDJEC: "./attached_assets/photos/",
  BAZA_ODMIAN: "./wina/",

  /** Jedyna funkcja formatująca kwoty w projekcie. */
  formatujCene(wartosc) {
    return `${Number(wartosc).toFixed(2)} zł`;
  },

  /** Slug odmiany → czytelna nazwa na chip „Szczep": "seyval-blanc" → "Seyval Blanc". */
  humanizujSlug(slug) {
    return String(slug ?? "")
      .replace(/-/g, " ")
      .replace(/\b\w/g, (znak) => znak.toUpperCase());
  },

  /**
   * Zapisana jest wyłącznie cena brutto — netto i cena sprzed rabatu są wyliczane.
   * Patrz .ai/standards/content/wina-json.md.
   */
  policzCeny(wino, stawkaVat) {
    const brutto = Number(wino.cena_brutto || 0);
    const rabat = Number(wino.rabat_procent || 0);
    return {
      brutto,
      netto: brutto / (1 + Number(stawkaVat || 0)),
      przedRabatem: rabat > 0 ? brutto / (1 - rabat / 100) : null,
      promocja: rabat > 0,
    };
  },

  /** Części podpisu pod nazwą: ["2024", "12.0% alk.", "750 ml"] */
  opisPodtytul(wino) {
    const czesci = [];
    if (wino.rocznik) czesci.push(String(wino.rocznik));
    if (wino.alkohol) czesci.push(`${Number(wino.alkohol).toFixed(1)}% alk.`);
    if (wino.pojemnosc_ml) {
      const ml = Number(wino.pojemnosc_ml);
      // od 1000 ml podajemy litry, po polsku z przecinkiem: 1500 → "1,5 l"
      czesci.push(ml >= 1000 ? `${String(ml / 1000).replace(".", ",")} l` : `${ml} ml`);
    }
    return czesci;
  },

  /** Nowe zdjęcie sklepu może wskazywać plik bezpośrednio pod attached_assets/. */
  sciezkaZdjecia(wino, bazaZdjec = this.BAZA_ZDJEC) {
    if (wino.zdjecie_sklep) {
      const bazaZasobow = bazaZdjec.replace(/photos\/?$/, "");
      const sciezka = String(wino.zdjecie_sklep)
        .replace(/^\/?\.?\/?attached_assets\//, "")
        .replace(/^\/+/, "");
      return `${bazaZasobow}${this.escape(sciezka)}`;
    }
    return `${bazaZdjec}${this.escape(wino.zdjecie)}-sm.jpg`;
  },

  /**
   * Zwraca STRING z HTML-em jednej karty produktu (nie węzeł DOM).
   * opcje: { linkOdmiany = true, przyciskKoszyka = true, bazaZdjec = BAZA_ZDJEC }
   *
   * Klasy CSS muszą pozostać takie, jak w bundlu Tailwinda — nowej klasy utility
   * nie da się dobudować (.ai/standards/frontend/styling.md).
   */
  renderProductCard(wino, stawkaVat, opcje = {}) {
    const {
      linkOdmiany = true, przyciskKoszyka = true, pokazNetto = true,
      bazaZdjec = this.BAZA_ZDJEC, bazaOdmian = this.BAZA_ODMIAN,
    } = opcje;
    const ceny = this.policzCeny(wino, stawkaVat);
    const zdjecie = this.sciezkaZdjecia(wino, bazaZdjec);
    const nazwa = this.escape(wino.nazwa);

    const kategoriaBadge = `<span class="chip">${this.escape(wino.kategoria)}</span>`;
    // Soki nie mają szczepu — ukrywamy cały wiersz „Szczep:", nie tylko chip.
    const maSzczep = wino.odmiana_slug && wino.kategoria !== "Soki";
    const szczepNazwa = maSzczep ? this.escape(this.humanizujSlug(wino.odmiana_slug)) : "";
    const szczepChip = !maSzczep
      ? ""
      : linkOdmiany
        ? `<a href="${bazaOdmian}${this.escape(wino.odmiana_slug)}.html" class="chip chip-link" title="Dowiedz się więcej o szczepie ${szczepNazwa}">${szczepNazwa}</a>`
        : `<span class="chip">${szczepNazwa}</span>`;
    const szczepWiersz = maSzczep
      ? `<div class="flex flex-wrap items-center gap-2 mb-4">
                      <span class="chip-etykieta">Szczep:</span>
                      ${szczepChip}
                    </div>`
      : "";
    const badgePromo = ceny.promocja
      ? `<span class="inline-flex items-center rounded-md bg-ring text-primary font-semibold px-3 py-1 text-xs">-${Number(wino.rabat_procent)}%</span>`
      : "";
    const rodzajBadge = wino.rodzaj
      ? `<span class="chip">${this.escape(wino.rodzaj)}</span>`
      : "";
    const cenaPrzed = ceny.przedRabatem
      ? `<span class="text-m text-muted-foreground line-through">${this.formatujCene(ceny.przedRabatem)}</span>`
      : "";
    const kolorCeny = ceny.promocja ? "text-ring" : "text-foreground";
    // Nieescapowane części z opisPodtytul(); escape dopiero tu, bo wynik idzie do innerHTML.
    const czesciPodpisu = this.opisPodtytul(wino).map((czesc) => this.escape(czesc));
    const podpisTytulu = czesciPodpisu.length
      ? `<p class="podpis-tytulu font-serif text-xl mb-4" style="margin-top: -0.25rem;">${czesciPodpisu.join(' <span class="bullet-mniejszy">•</span> ')}</p>`
      : "";
    const przycisk = przyciskKoszyka
      ? `<div style="margin-top: 1rem;"><button class="btn-primary w-full flex items-center justify-center gap-2" data-add-to-cart><svg class="w-4 h-4"><use href="#icon-cart"></use></svg>Dodaj</button></div>`
      : "";
    const netto = pokazNetto
      ? `<span class="netto-cena text-muted-foreground"><span class="netto-etykieta">netto:</span> ${this.formatujCene(ceny.netto)}</span>`
      : "";

    return `
                <article class="product-card rounded-md border border-card-border overflow-hidden hover-elevate h-full flex flex-col" data-id="${this.escape(wino.id)}" data-category="${this.escape(wino.kategoria)}" data-price="${ceny.brutto.toFixed(2)}" data-promo="${ceny.promocja}" data-name="${nazwa}" data-image="${this.escape(zdjecie)}">
                  <div class="relative aspect-[3/4] bg-secondary/30 overflow-hidden">
                    <img src="${this.escape(zdjecie)}" alt="${nazwa}" class="w-full h-full object-cover" loading="lazy">
                  </div>
                  <div class="p-5 flex flex-col flex-1">
                    <h3 class="font-serif text-3xl font-semibold mb-2">${nazwa}</h3>
                    ${podpisTytulu}
                    <div class="mb-5">
                      <p class="opis-karta text-muted-foreground text-lg">${this.escape(wino.opis)}</p>
                      <button type="button" class="opis-wiecej p-1" data-opis-wiecej>więcej</button>
                    </div>
                    <div class="flex flex-wrap items-center gap-2 mb-4">
                      <span class="chip-etykieta">Rodzaj:</span>
                      ${kategoriaBadge}
                      ${rodzajBadge}
                    </div>
                    ${szczepWiersz}
                    <div class="flex flex-col" style="margin-top: auto;">
                      ${cenaPrzed}
                      <div class="flex items-baseline justify-between gap-2">
                        <span class="text-3xl font-bold ${kolorCeny}">${this.formatujCene(ceny.brutto)}</span>
                        ${badgePromo}
                      </div>
                      ${netto}
                    </div>
                    ${przycisk}
                  </div>
                </article>`;
  },

  /** Dane pochodzą z pliku edytowanego ręcznie — nie wstrzykujemy ich do HTML bez ucieczki. */
  escape(wartosc) {
    return String(wartosc ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },
};
