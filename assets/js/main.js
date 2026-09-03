const themeStyles = {
  classic: {
    name: "Classic Burgundy",
    colorScheme: "light",
    vars: {
      "--background": "50 5% 98%",
      "--foreground": "0 0% 18%",
      "--border": "39 10% 88%",
      "--card": "39 15% 96%",
      "--card-foreground": "0 0% 18%",
      "--card-border": "39 12% 92%",
      "--sidebar": "39 18% 94%",
      "--sidebar-foreground": "0 0% 18%",
      "--sidebar-border": "39 15% 90%",
      "--sidebar-primary": "0 100% 27%",
      "--sidebar-primary-foreground": "39 77% 95%",
      "--sidebar-accent": "39 20% 88%",
      "--sidebar-accent-foreground": "0 0% 18%",
      "--sidebar-ring": "43 74% 49%",
      "--popover": "39 22% 92%",
      "--popover-foreground": "0 0% 18%",
      "--popover-border": "39 18% 88%",
      "--primary": "0 100% 27%",
      "--primary-foreground": "39 77% 95%",
      "--secondary": "39 25% 86%",
      "--secondary-foreground": "0 0% 18%",
      "--muted": "39 20% 90%",
      "--muted-foreground": "0 0% 35%",
      "--accent": "39 25% 88%",
      "--accent-foreground": "0 0% 18%",
      "--destructive": "0 84% 45%",
      "--destructive-foreground": "0 0% 98%",
      "--input": "0 0% 65%",
      "--ring": "43 74% 49%"
    }
  },
  modern: {
    name: "Modern Minimal",
    colorScheme: "dark",
    vars: {
      "--background": "225 12% 8%",
      "--foreground": "40 20% 94%",
      "--border": "220 10% 24%",
      "--card": "225 11% 11%",
      "--card-foreground": "40 20% 94%",
      "--card-border": "220 10% 19%",
      "--sidebar": "225 12% 10%",
      "--sidebar-foreground": "40 20% 94%",
      "--sidebar-border": "220 10% 20%",
      "--sidebar-primary": "38 60% 54%",
      "--sidebar-primary-foreground": "225 14% 8%",
      "--sidebar-accent": "220 10% 18%",
      "--sidebar-accent-foreground": "40 20% 94%",
      "--sidebar-ring": "38 70% 58%",
      "--popover": "225 12% 12%",
      "--popover-foreground": "40 20% 94%",
      "--popover-border": "220 10% 22%",
      "--primary": "220 11% 16%",
      "--primary-foreground": "40 20% 96%",
      "--secondary": "220 10% 17%",
      "--secondary-foreground": "40 15% 92%",
      "--muted": "220 9% 14%",
      "--muted-foreground": "215 12% 68%",
      "--accent": "220 10% 20%",
      "--accent-foreground": "40 20% 96%",
      "--destructive": "0 68% 46%",
      "--destructive-foreground": "0 0% 98%",
      "--input": "220 10% 35%",
      "--ring": "38 70% 58%"
    }
  },
  rustic: {
    name: "Rustic Natural",
    colorScheme: "light",
    vars: {
      "--background": "32 25% 96%",
      "--foreground": "25 20% 15%",
      "--border": "30 15% 82%",
      "--card": "35 30% 92%",
      "--card-foreground": "25 20% 15%",
      "--card-border": "32 18% 86%",
      "--sidebar": "30 25% 88%",
      "--sidebar-foreground": "25 20% 15%",
      "--sidebar-border": "30 20% 80%",
      "--sidebar-primary": "25 45% 35%",
      "--sidebar-primary-foreground": "35 30% 95%",
      "--sidebar-accent": "32 22% 84%",
      "--sidebar-accent-foreground": "25 20% 15%",
      "--sidebar-ring": "35 60% 45%",
      "--popover": "32 28% 90%",
      "--popover-foreground": "25 20% 15%",
      "--popover-border": "30 18% 84%",
      "--primary": "25 45% 35%",
      "--primary-foreground": "35 30% 95%",
      "--secondary": "32 25% 85%",
      "--secondary-foreground": "25 20% 15%",
      "--muted": "32 20% 88%",
      "--muted-foreground": "25 15% 40%",
      "--accent": "35 30% 82%",
      "--accent-foreground": "25 20% 15%",
      "--destructive": "0 84% 45%",
      "--destructive-foreground": "0 0% 98%",
      "--input": "0 0% 65%",
      "--ring": "35 60% 45%"
    }
  }
};

const cart = new Map();

// Cennik z data/wina.json — jedyne źródło asortymentu i cen.
// Patrz .ai/standards/content/wina-json.md
let cennik = null;
const STAWKA_VAT_DOMYSLNA = 0.23;

// Korzen witryny liczony z adresu tego skryptu (assets/js/main.js). Dzieki temu
// te same pliki dzialaja na stronie glownej i w podkatalogu wina/, a takze gdyby
// witryna kiedys stanela w podkatalogu domeny.
const KORZEN = (() => {
  const skrypt = document.querySelector('script[src$="main.js"]');
  return skrypt ? new URL("../../", skrypt.src).href : "/";
})();

function stawkaVat() {
  return cennik?.stawka_vat ?? STAWKA_VAT_DOMYSLNA;
}

const qs = (sel) => document.querySelector(sel);
const qsa = (sel) => Array.from(document.querySelectorAll(sel));

function setTheme(style, persist = true) {
  const theme = themeStyles[style];
  if (!theme) return;
  const root = document.documentElement;
  Object.entries(theme.vars).forEach(([key, value]) => root.style.setProperty(key, value));
  root.style.colorScheme = theme.colorScheme;
  if (persist) localStorage.setItem("winery-style", style);
  updateStyleMenu(style);
}

function updateStyleMenu(style) {
  qsa(".style-option").forEach((btn) => {
    const isActive = btn.dataset.style === style;
    btn.querySelector("svg")?.classList.toggle("hidden", !isActive);
  });
}

function preferredTheme() {
  const saved = localStorage.getItem("winery-style");
  return themeStyles[saved] ? saved : "classic";
}

function initStyleSwitcher() {
  const trigger = qs("#style-trigger");
  const menu = qs("#style-menu");
  setTheme(preferredTheme(), false);

  trigger?.addEventListener("click", () => {
    menu?.classList.toggle("hidden");
  });

  document.addEventListener("click", (e) => {
    if (!menu || !trigger) return;
    if (menu.contains(e.target) || trigger.contains(e.target)) return;
    menu.classList.add("hidden");
  });

  qsa(".style-option").forEach((btn) =>
    btn.addEventListener("click", () => {
      const style = btn.dataset.style;
      if (style) {
        setTheme(style);
        menu?.classList.add("hidden");
      }
    })
  );
}

function heroPeriodForHour(hour) {
  if (!Number.isInteger(hour) || hour < 0 || hour > 23) return null;
  if (hour >= 6 && hour < 12) return "poranek";
  if (hour >= 12 && hour < 18) return "dzien";
  if (hour >= 18 && hour < 22) return "zachod";
  return "noc";
}

function wineryHour() {
  try {
    const parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: "Europe/Warsaw",
      hour: "numeric",
      hourCycle: "h23"
    }).formatToParts(new Date());
    const hour = Number.parseInt(parts.find((part) => part.type === "hour")?.value, 10);
    if (Number.isInteger(hour) && hour >= 0 && hour <= 23) return hour;
  } catch (_) {
    // Starsza przeglądarka może nie znać stref IANA — wtedy używamy czasu urządzenia.
  }
  return new Date().getHours();
}

/** Pora wymuszona adresem (?hero=noc) — narzedzie testowe, patrz initPrzelacznikHero. */
function wymuszonaPoraHero() {
  const zadana = new URLSearchParams(location.search).get("hero");
  return ["poranek", "dzien", "zachod", "noc"].includes(zadana) ? zadana : null;
}

function initHeroImage() {
  const image = qs("#hero-image");
  if (!image) return;

  const wymuszona = wymuszonaPoraHero();

  const fallbackSrc = image.dataset.fallbackSrc;
  let selectedPeriod = null;
  let selectedSrc = null;
  let failedSrc = null;

  image?.addEventListener("error", () => {
    const currentSrc = image.getAttribute("src");
    if (!currentSrc || currentSrc === fallbackSrc) return;
    failedSrc = currentSrc;
    if (fallbackSrc) image.setAttribute("src", fallbackSrc);
  });

  function updateImage() {
    const period = wymuszona || heroPeriodForHour(wineryHour());
    const nextSrc = period ? image.dataset[`${period}Src`] : null;
    if (!nextSrc) return;

    if (period !== selectedPeriod) {
      const wasNight = selectedPeriod === "noc";
      selectedPeriod = period;
      if (period === "noc") setTheme("modern", false);
      else if (wasNight) setTheme(preferredTheme(), false);
    }

    if (nextSrc !== selectedSrc) {
      selectedSrc = nextSrc;
      failedSrc = null;
    }
    if (nextSrc !== failedSrc && image.getAttribute("src") !== nextSrc) {
      image.setAttribute("src", nextSrc);
    }
  }

  updateImage();
  // Przy wymuszonej porze zegar jest zbedny — inaczej po minucie nadpisalby wybor.
  if (!wymuszona) window.setInterval(updateImage, 60_000);
}

function initNavigation() {
  const mobileToggle = qs("#mobile-menu-toggle");
  const mobileMenu = qs("#mobile-menu");

  qsa("[data-scroll]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-scroll");
      const el = target ? qs(target) : null;
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
        mobileMenu?.classList.add("hidden");
        const icon = mobileToggle?.querySelector("use");
        if (icon) icon.setAttribute("href", "#icon-menu");
      }
    });
  });

  mobileToggle?.addEventListener("click", () => {
    const opened = mobileMenu?.classList.toggle("hidden");
    const icon = mobileToggle.querySelector("use");
    if (icon) icon.setAttribute("href", opened ? "#icon-menu" : "#icon-close");
  });
}

function initFilters() {
  const categorySelect = qs("#category-select");
  const priceMin = qs("#price-min");
  const priceMax = qs("#price-max");
  const priceMinLabel = qs("#price-min-label");
  const priceMaxLabel = qs("#price-max-label");
  const promoOnly = qs("#promo-only");
  const clearBtn = qs("#clear-filters");
  const activeFilters = qs("#active-filters");
  const filterCategory = qs("#filter-category");
  const filterPromo = qs("#filter-promo");
  const rangeHighlight = qs("#range-highlight");
  const noProducts = qs("#no-products");
  const products = qsa(".product-card");

  // Granice suwaka biorą się z danych, nie z zaszytego 0–100 (TODO.md #2).
  const zakres = zakresCen();
  [priceMin, priceMax].forEach((input) => {
    if (!input) return;
    input.min = String(zakres.min);
    input.max = String(zakres.max);
  });
  if (priceMin) priceMin.value = String(zakres.min);
  if (priceMax) priceMax.value = String(zakres.max);
  if (priceMinLabel) priceMinLabel.textContent = String(zakres.min);
  if (priceMaxLabel) priceMaxLabel.textContent = String(zakres.max);

  function procent(wartosc) {
    const rozpietosc = zakres.max - zakres.min;
    return rozpietosc > 0 ? ((wartosc - zakres.min) / rozpietosc) * 100 : 0;
  }

  function updateHighlight() {
    if (!priceMin || !priceMax || !rangeHighlight) return;
    const minPercent = procent(Number(priceMin.value));
    const maxPercent = procent(Number(priceMax.value));
    rangeHighlight.style.background = `linear-gradient(to right, hsl(var(--secondary)) 0%, hsl(var(--secondary)) ${minPercent}%, hsl(var(--primary)) ${minPercent}%, hsl(var(--primary)) ${maxPercent}%, hsl(var(--secondary)) ${maxPercent}%, hsl(var(--secondary)) 100%)`;
  }

  function toggleBadge(el, visible, label) {
    if (!el) return;
    el.classList.toggle("hidden", !visible);
    if (visible && label) {
      const textHolder = el.querySelector("span");
      if (textHolder) textHolder.textContent = label;
    }
  }

  function applyFilters() {
    const category = categorySelect?.value || "Wszystkie";
    const min = Number(priceMin?.value ?? zakres.min);
    const max = Number(priceMax?.value ?? zakres.max);
    const promo = promoOnly?.checked || false;

    let visible = 0;
    products.forEach((card) => {
      const price = Number(card.dataset.price || 0);
      const cardCategory = card.dataset.category || "";
      const isPromo = card.dataset.promo === "true";
      const matchesCategory = category === "Wszystkie" || cardCategory === category;
      const matchesPrice = price >= min && price <= max;
      const matchesPromo = !promo || isPromo;
      const shouldShow = matchesCategory && matchesPrice && matchesPromo;
      card.classList.toggle("hidden", !shouldShow);
      if (shouldShow) visible += 1;
    });

    const hasFilters =
      category !== "Wszystkie" || promo || min > zakres.min || max < zakres.max;
    clearBtn?.classList.toggle("hidden", !hasFilters);
    activeFilters?.classList.toggle("hidden", !hasFilters);
    toggleBadge(filterCategory, category !== "Wszystkie", category);
    toggleBadge(filterPromo, promo, "Promocje");
    noProducts?.classList.toggle("hidden", visible > 0);
  }

  function handleRangeChange(e) {
    if (!priceMin || !priceMax || !priceMinLabel || !priceMaxLabel) return;
    let min = Number(priceMin.value);
    let max = Number(priceMax.value);
    if (min > max) {
      if (e.target === priceMin) priceMax.value = String(min);
      else priceMin.value = String(max);
      min = Number(priceMin.value);
      max = Number(priceMax.value);
    }
    priceMinLabel.textContent = min.toString();
    priceMaxLabel.textContent = max.toString();
    updateHighlight();
    applyFilters();
  }

  priceMin?.addEventListener("input", handleRangeChange);
  priceMax?.addEventListener("input", handleRangeChange);
  priceMin?.addEventListener("change", handleRangeChange);
  priceMax?.addEventListener("change", handleRangeChange);

  categorySelect?.addEventListener("change", applyFilters);
  promoOnly?.addEventListener("change", applyFilters);

  clearBtn?.addEventListener("click", () => {
    if (categorySelect) categorySelect.value = "Wszystkie";
    if (priceMin) priceMin.value = String(zakres.min);
    if (priceMax) priceMax.value = String(zakres.max);
    if (promoOnly) promoOnly.checked = false;
    priceMinLabel && (priceMinLabel.textContent = String(zakres.min));
    priceMaxLabel && (priceMaxLabel.textContent = String(zakres.max));
    updateHighlight();
    applyFilters();
  });

  filterCategory?.querySelector("button")?.addEventListener("click", () => {
    if (categorySelect) categorySelect.value = "Wszystkie";
    applyFilters();
  });

  filterPromo?.querySelector("button")?.addEventListener("click", () => {
    if (promoOnly) promoOnly.checked = false;
    applyFilters();
  });

  updateHighlight();
  applyFilters();
}

function renderCart() {
  const overlay = qs("#cart-overlay");
  const itemsWrap = qs("#cart-items");
  const emptyState = qs("#cart-empty");
  const summary = qs("#cart-summary");
  const countLabel = qs("#cart-count");
  const itemsCount = qs("#cart-items-count");
  const subtotalEl = qs("#cart-subtotal");
  const taxEl = qs("#cart-tax");
  const totalEl = qs("#cart-total");

  const items = Array.from(cart.values());
  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const net = subtotal / (1 + stawkaVat());
  const tax = subtotal - net;
  const taxLabel = qs("#cart-tax-label");
  if (taxLabel) taxLabel.textContent = `VAT (${Math.round(stawkaVat() * 100)}%):`;

  if (countLabel) {
    if (totalItems > 0) {
      countLabel.textContent = String(totalItems);
      countLabel.classList.remove("hidden");
      countLabel.classList.add("flex");
    } else {
      countLabel.classList.add("hidden");
      countLabel.classList.remove("flex");
    }
  }

  if (itemsCount) itemsCount.textContent = `(${items.length})`;
  if (subtotalEl) subtotalEl.textContent = Produkty.formatujCene(net);
  if (taxEl) taxEl.textContent = Produkty.formatujCene(tax);
  if (totalEl) totalEl.textContent = Produkty.formatujCene(subtotal);

  if (!itemsWrap || !emptyState || !summary) return;

  if (items.length === 0) {
    emptyState.classList.remove("hidden");
    itemsWrap.classList.add("hidden");
    summary.classList.add("hidden");
    return;
  }

  emptyState.classList.add("hidden");
  itemsWrap.classList.remove("hidden");
  summary.classList.remove("hidden");

  itemsWrap.innerHTML = items
    .map(
      (item) => `
      <div class="cart-item" data-id="${item.id}">
        <div class="w-20 h-20 bg-secondary/30 rounded-md overflow-hidden flex-shrink-0">
          <img src="${item.image}" alt="${item.name}" class="w-full h-full object-contain p-2">
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2 mb-2">
            <h4 class="font-medium line-clamp-2">${item.name}</h4>
            <button class="w-8 h-8 inline-flex items-center justify-center rounded-md hover:bg-muted" data-remove="${item.id}">
              <svg class="w-4 h-4"><use href="#icon-close"></use></svg>
            </button>
          </div>
          <div class="flex items-center justify-between gap-3">
            <div class="quantity-control">
              <button data-decrease="${item.id}"><svg class="w-3 h-3"><use href="#icon-minus"></use></svg></button>
              <span>${item.quantity}</span>
              <button data-increase="${item.id}"><svg class="w-3 h-3"><use href="#icon-plus"></use></svg></button>
            </div>
            <span class="font-semibold">${Produkty.formatujCene(item.price * item.quantity)}</span>
          </div>
        </div>
      </div>
    `
    )
    .join("");

  itemsWrap.querySelectorAll("[data-remove]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-remove");
      if (id) {
        cart.delete(id);
        renderCart();
      }
    })
  );

  itemsWrap.querySelectorAll("[data-decrease]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-decrease");
      if (!id || !cart.has(id)) return;
      const entry = cart.get(id);
      entry.quantity = Math.max(1, entry.quantity - 1);
      cart.set(id, entry);
      renderCart();
    })
  );

  itemsWrap.querySelectorAll("[data-increase]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-increase");
      if (!id || !cart.has(id)) return;
      const entry = cart.get(id);
      entry.quantity += 1;
      cart.set(id, entry);
      renderCart();
    })
  );
}

function openCart() {
  document.body.classList.add("cart-open");
}

function closeCart() {
  document.body.classList.remove("cart-open");
}

function initCart() {
  const cartButton = qs("#cart-button");
  const overlay = qs("#cart-overlay");
  const closeBtn = qs("#close-cart");
  const checkout = qs("#checkout");

  cartButton?.addEventListener("click", () => {
    openCart();
  });

  overlay?.addEventListener("click", closeCart);
  closeBtn?.addEventListener("click", closeCart);

  checkout?.addEventListener("click", () => {
    if (cart.size === 0) return;
    alert("Przekierowanie do płatności w pełnej wersji sklepu.");
  });

  // Delegacja: karty produktów powstają dopiero po wczytaniu cennika i mogą
  // zostać przerenderowane, więc nasłuch wisi na kontenerze, nie na przyciskach.
  qs("#lista-produktow")?.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-add-to-cart]");
    if (btn) {
      const card = btn.closest(".product-card");
      if (!card) return;
      const id = card.dataset.id;
      if (!id) return;
      const price = Number(card.dataset.price || 0);
      const name = card.dataset.name || "Produkt";
      const image = card.dataset.image || "";
      if (cart.has(id)) {
        const entry = cart.get(id);
        entry.quantity += 1;
        cart.set(id, entry);
      } else {
        cart.set(id, { id, name, price, image, quantity: 1 });
      }
      renderCart();
      openCart();
    }
  });

  renderCart();
}

/** Wczytuje data/wina.json. Zwraca null, jeśli się nie udało — komunikat pokazuje initShop. */
async function wczytajCennik() {
  try {
    const odpowiedz = await fetch(`${KORZEN}data/wina.json`, { cache: "no-store" });
    if (!odpowiedz.ok) throw new Error(`HTTP ${odpowiedz.status}`);
    const dane = await odpowiedz.json();
    if (!Array.isArray(dane?.wina)) throw new Error("brak tablicy 'wina'");
    return dane;
  } catch (blad) {
    console.error("Nie udało się wczytać data/wina.json:", blad);
    return null;
  }
}

/** Zakres suwaka cen liczony z danych; sensowny domyślny, gdy cennik jest pusty. */
function zakresCen() {
  const ceny = (cennik?.wina || [])
    .filter((wino) => wino.dostepne !== false)
    .map((wino) => Number(wino.cena_brutto || 0));
  if (ceny.length === 0) return { min: 0, max: 100 };
  return { min: Math.floor(Math.min(...ceny)), max: Math.ceil(Math.max(...ceny)) };
}

/** Opcje filtra kategorii biorą się z cennika — dodanie kategorii nie wymaga zmian w HTML. */
function renderKategorie() {
  const select = qs("#category-select");
  if (!select) return;
  const kategorie = cennik?.kategorie || [];
  select.innerHTML = ["Wszystkie", ...kategorie]
    .map((nazwa) => `<option>${Produkty.escape(nazwa)}</option>`)
    .join("");
}

function komunikatSklepu(tresc) {
  const wrap = qs("#lista-produktow");
  if (!wrap) return;
  wrap.innerHTML = `
                <p class="col-span-full text-center text-muted-foreground py-12">${tresc}</p>`;
}

/**
 * Buduje sekcję sklepu z cennika. Bez tego kroku nie ma czego filtrować,
 * dlatego initFilters() uruchamia się dopiero po nim.
 */
function renderSklep() {
  const wrap = qs("#lista-produktow");
  if (!wrap) return false;

  if (!cennik) {
    komunikatSklepu(
      'Nie udało się wczytać oferty. <a href="#kontakt" class="underline">Skontaktuj się z nami</a>.'
    );
    return false;
  }

  const kategorie = cennik.kategorie || [];
  const dostepne = cennik.wina.filter((wino) => {
    if (wino.dostepne === false) return false;
    if (!kategorie.includes(wino.kategoria)) {
      console.warn(`Pomijam "${wino.id}" — nieznana kategoria "${wino.kategoria}"`);
      return false;
    }
    return true;
  });

  if (dostepne.length === 0) {
    komunikatSklepu("Oferta w przygotowaniu — zapraszamy wkrótce.");
    return false;
  }

  wrap.innerHTML = dostepne
    .map((wino) => Produkty.renderProductCard(wino, stawkaVat(), {
      bazaZdjec: `${KORZEN}attached_assets/photos/`,
      bazaOdmian: `${KORZEN}wina/`,
    }))
    .join("");
  return true;
}

/** Blok „Wina z tej odmiany" na stronach odmian. Treść strony działa bez tego. */
function initWineOffer() {
  const wrap = qs("#oferta-odmiany");
  if (!wrap) return;
  const slug = wrap.dataset.odmiana;
  const pasujace = (cennik?.wina || []).filter((wino) => wino.odmiana_slug === slug);

  if (pasujace.length === 0) return; // zostaje statyczny tekst zastępczy z HTML-a

  wrap.innerHTML = pasujace
    .map((wino) => {
      const ceny = Produkty.policzCeny(wino, stawkaVat());
      const opis = Produkty.opisPodtytul(wino).join(" • ");
      const cena = wino.dostepne === false
        ? '<span class="text-muted-foreground">chwilowo niedostępne</span>'
        : `<span class="text-xl font-bold text-ring">${Produkty.formatujCene(ceny.brutto)}</span>`;
      return `
          <div class="flex flex-wrap items-center justify-between gap-4 border-b border-border py-4 last:border-0">
            <div>
              <p class="font-semibold">${Produkty.escape(wino.nazwa)}</p>
              <p class="text-sm text-muted-foreground">${Produkty.escape(opis)}</p>
            </div>
            <div class="flex items-center gap-4">${cena}
              <a href="${KORZEN}index.html#sklep" class="btn-primary">Zobacz w sklepie</a>
            </div>
          </div>`;
    })
    .join("");
}

/**
 * Pasek wyboru zdjęcia wejściowego — narzędzie testowe, nie funkcja witryny.
 *
 * Pokazuje się WYŁĄCZNIE gdy serwer doda body[data-hero-kandydaci], czyli gdy adres
 * zawiera ?hero. Zwykły odwiedzający nigdy go nie zobaczy i nic go nie kosztuje.
 *
 * Sama podmiana zdjęcia dzieje się po stronie serwera (wsgi.py), więc wynik pomiaru
 * w PageSpeed dotyczy naprawdę wybranego zdjęcia, a nie domyślnego z podmianą w locie.
 *
 * Celowo bez miniatur: podgląd czterech kadrów oznaczałby pobranie ~8,4 MB grafiki
 * i zafałszowanie pomiaru, dla którego ten pasek w ogóle powstał.
 */
function initPrzelacznikHero() {
  const kandydaci = document.body.dataset.heroKandydaci;
  if (!kandydaci) return;

  const wybrana = wymuszonaPoraHero();
  const opisy = { poranek: "Poranek", dzien: "Dzień", zachod: "Zachód", noc: "Noc" };

  const pasek = document.createElement("div");
  pasek.className = "przelacznik-hero";
  pasek.innerHTML =
    '<span class="przelacznik-hero__tytul">Zdjęcie wejściowe</span>' +
    kandydaci
      .split(",")
      .map((pora) => {
        const aktywna = pora === wybrana ? " przelacznik-hero__opcja--aktywna" : "";
        return `<a class="przelacznik-hero__opcja${aktywna}" href="?hero=${pora}">${
          opisy[pora] || pora
        }</a>`;
      })
      .join("") +
    `<a class="przelacznik-hero__opcja" href="./">${wybrana ? "Wróć do pory dnia" : "Zamknij"}</a>`;
  document.body.appendChild(pasek);
}

function initContactForm() {
  const form = qs("#contact-form");
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Dziękujemy za wiadomość! Skontaktujemy się wkrótce.");
    form.reset();
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  initStyleSwitcher();
  initHeroImage();
  initNavigation();
  initContactForm();
  initPrzelacznikHero();

  cennik = await wczytajCennik();
  renderKategorie();
  if (renderSklep()) initFilters();
  initWineOffer();
  initCart();
});
