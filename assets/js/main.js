const themeStyles = {
  classic: {
    name: "Classic Burgundy",
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
    vars: {
      "--background": "0 0% 98%",
      "--foreground": "0 0% 10%",
      "--border": "0 0% 88%",
      "--card": "0 0% 100%",
      "--card-foreground": "0 0% 10%",
      "--card-border": "0 0% 92%",
      "--sidebar": "0 0% 96%",
      "--sidebar-foreground": "0 0% 10%",
      "--sidebar-border": "0 0% 90%",
      "--sidebar-primary": "0 0% 15%",
      "--sidebar-primary-foreground": "0 0% 98%",
      "--sidebar-accent": "0 0% 92%",
      "--sidebar-accent-foreground": "0 0% 10%",
      "--sidebar-ring": "0 0% 30%",
      "--popover": "0 0% 98%",
      "--popover-foreground": "0 0% 10%",
      "--popover-border": "0 0% 88%",
      "--primary": "0 0% 15%",
      "--primary-foreground": "0 0% 98%",
      "--secondary": "0 0% 92%",
      "--secondary-foreground": "0 0% 10%",
      "--muted": "0 0% 94%",
      "--muted-foreground": "0 0% 40%",
      "--accent": "0 0% 90%",
      "--accent-foreground": "0 0% 10%",
      "--destructive": "0 84% 45%",
      "--destructive-foreground": "0 0% 98%",
      "--input": "0 0% 65%",
      "--ring": "0 0% 30%"
    }
  },
  rustic: {
    name: "Rustic Natural",
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

const qs = (sel) => document.querySelector(sel);
const qsa = (sel) => Array.from(document.querySelectorAll(sel));

function setTheme(style) {
  const vars = themeStyles[style]?.vars;
  if (!vars) return;
  const root = document.documentElement;
  Object.entries(vars).forEach(([key, value]) => root.style.setProperty(key, value));
  localStorage.setItem("winery-style", style);
  updateStyleMenu(style);
}

function updateStyleMenu(style) {
  qsa(".style-option").forEach((btn) => {
    const isActive = btn.dataset.style === style;
    btn.querySelector("svg")?.classList.toggle("hidden", !isActive);
  });
}

function initStyleSwitcher() {
  const trigger = qs("#style-trigger");
  const menu = qs("#style-menu");
  const saved = localStorage.getItem("winery-style") || "classic";
  setTheme(saved);

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

  function updateHighlight() {
    if (!priceMin || !priceMax || !rangeHighlight) return;
    const minVal = Number(priceMin.value);
    const maxVal = Number(priceMax.value);
    const minPercent = (minVal / 100) * 100;
    const maxPercent = (maxVal / 100) * 100;
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
    const min = Number(priceMin?.value || 0);
    const max = Number(priceMax?.value || 100);
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

    const hasFilters = category !== "Wszystkie" || promo || min > 0 || max < 100;
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
    if (priceMin) priceMin.value = "0";
    if (priceMax) priceMax.value = "100";
    if (promoOnly) promoOnly.checked = false;
    priceMinLabel && (priceMinLabel.textContent = "0");
    priceMaxLabel && (priceMaxLabel.textContent = "100");
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

function formatPrice(value) {
  return `${value.toFixed(2)} zł`;
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
  const net = subtotal / 1.23;
  const tax = subtotal - net;

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
  if (subtotalEl) subtotalEl.textContent = formatPrice(net);
  if (taxEl) taxEl.textContent = formatPrice(tax);
  if (totalEl) totalEl.textContent = formatPrice(subtotal);

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
            <span class="font-semibold">${formatPrice(item.price * item.quantity)}</span>
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

  qsa("[data-add-to-cart]").forEach((btn) =>
    btn.addEventListener("click", () => {
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
    })
  );

  renderCart();
}

function initContactForm() {
  const form = qs("#contact-form");
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Dziękujemy za wiadomość! Skontaktujemy się wkrótce.");
    form.reset();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initStyleSwitcher();
  initNavigation();
  initFilters();
  initCart();
  initContactForm();
});
