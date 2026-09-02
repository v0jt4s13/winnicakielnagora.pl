/**
 * Biblioteka produktów — wyliczenia cen i render karty.
 *
 * Ładowana PRZED main.js. Nie rejestruje zdarzeń i nie dotyka DOM-u przy wczytaniu,
 * dzięki czemu używa jej także panel redakcyjny (tools/panel/) do podglądu karty.
 * Patrz .ai/GUARDRAILS.md → "Front-end bez frameworka i bez modułów, w dwóch plikach".
 */
const Produkty = {
  BAZA_ZDJEC: "./attached_assets/photos/",

  /** Jedyna funkcja formatująca kwoty w projekcie. */
  formatujCene(wartosc) {
    return `${Number(wartosc).toFixed(2)} zł`;
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

  /** Podpis pod nazwą: "Rocznik 2024 • 12.0% alk." — pomijany w całości dla soków. */
  opisPodtytul(wino) {
    const czesci = [];
    if (wino.rocznik) czesci.push(`Rocznik ${wino.rocznik}`);
    if (wino.alkohol) czesci.push(`${Number(wino.alkohol).toFixed(1)}% alk.`);
    if (wino.pojemnosc_ml) czesci.push(`${wino.pojemnosc_ml} ml`);
    return czesci;
  },

  /**
   * Zwraca STRING z HTML-em jednej karty produktu (nie węzeł DOM).
   * opcje: { linkOdmiany = true, przyciskKoszyka = true, bazaZdjec = BAZA_ZDJEC }
   *
   * Klasy CSS muszą pozostać takie, jak w bundlu Tailwinda — nowej klasy utility
   * nie da się dobudować (.ai/standards/frontend/styling.md).
   */
  renderProductCard(wino, stawkaVat, opcje = {}) {
    const { linkOdmiany = true, przyciskKoszyka = true, bazaZdjec = this.BAZA_ZDJEC } = opcje;
    const ceny = this.policzCeny(wino, stawkaVat);
    const zdjecie = `${bazaZdjec}${wino.zdjecie}-sm.jpg`;
    const nazwa = this.escape(wino.nazwa);

    const badgePromo = ceny.promocja
      ? `<span class="absolute top-3 right-3 inline-flex items-center rounded-md bg-ring text-primary font-semibold px-3 py-1 text-xs">-${Number(wino.rabat_procent)}%</span>`
      : "";
    const cenaPrzed = ceny.przedRabatem
      ? `<span class="text-sm text-muted-foreground line-through">${this.formatujCene(ceny.przedRabatem)}</span>`
      : "";
    const kolorCeny = ceny.promocja ? "text-ring" : "text-foreground";
    const podtytul = this.opisPodtytul(wino)
      .map((cz) => `<span>${this.escape(cz)}</span>`)
      .join("");
    const tytul = linkOdmiany
      ? `<a href="./wina/${this.escape(wino.odmiana_slug)}.html" class="hover:text-ring">${nazwa}</a>`
      : nazwa;
    const przycisk = przyciskKoszyka
      ? `<button class="btn-primary flex items-center gap-2" data-add-to-cart><svg class="w-4 h-4"><use href="#icon-cart"></use></svg>Dodaj</button>`
      : "";

    return `
                <article class="product-card rounded-md border border-card-border overflow-hidden hover-elevate" data-id="${this.escape(wino.id)}" data-category="${this.escape(wino.kategoria)}" data-price="${ceny.brutto.toFixed(2)}" data-promo="${ceny.promocja}" data-name="${nazwa}" data-image="${this.escape(zdjecie)}">
                  <div class="relative aspect-[3/4] bg-secondary/30">
                    <img src="${this.escape(zdjecie)}" alt="${nazwa}" class="w-full h-full object-contain p-8" loading="lazy">
                    <span class="absolute top-3 left-3 inline-flex items-center rounded-md bg-secondary px-3 py-1 text-xs font-semibold">${this.escape(wino.kategoria)}</span>
                    ${badgePromo}
                  </div>
                  <div class="p-5">
                    <h3 class="font-serif text-xl font-semibold mb-2">${tytul}</h3>
                    <p class="text-muted-foreground text-sm mb-3 line-clamp-2">${this.escape(wino.opis)}</p>
                    <div class="flex items-baseline gap-2 text-sm text-muted-foreground">${podtytul}</div>
                  </div>
                  <div class="p-5 pt-0 flex items-center justify-between gap-3">
                    <div class="flex flex-col">
                      ${cenaPrzed}
                      <div class="flex items-baseline gap-2"><span class="text-2xl font-bold ${kolorCeny}">${this.formatujCene(ceny.brutto)}</span></div>
                      <span class="text-xs text-muted-foreground">netto: ${this.formatujCene(ceny.netto)}</span>
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
