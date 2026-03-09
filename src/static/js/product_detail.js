"use strict";

let PD = null;

//  GALLERY
function switchImage(thumb) {
  const mainImg = document.getElementById("pd-main-img");
  const src = thumb.dataset.src;
  const alt = thumb.dataset.alt;

  mainImg.classList.add("swapping");
  setTimeout(function () {
    mainImg.src = src;
    mainImg.alt = alt;
    mainImg.classList.remove("swapping");
  }, 280);

  document.querySelectorAll(".pd-thumb").forEach(function (t) {
    t.classList.remove("active");
  });
  thumb.classList.add("active");
}

//  VARIATION PICKER
function selectVariation(btn) {
  if (btn.disabled) return;

  document.querySelectorAll(".pd-var-btn").forEach(function (b) {
    b.classList.remove("selected");
  });
  btn.classList.add("selected");

  const name = btn.dataset.varName;
  const price = btn.dataset.varPrice;
  const image = btn.dataset.varImage;
  const stock = btn.dataset.varStock === "true";

  const nameEl = document.getElementById("pd-var-name");
  if (nameEl) nameEl.textContent = name;

  updatePrice(price);
  if (image) swapVariationImage(image, name);
  updateCtaStock(stock);
}

function updatePrice(price) {
  const priceEl = document.getElementById("pd-price");
  const stickyPriceEl = document.getElementById("pd-sticky-price");
  const formatted = price ? "₦" + parseInt(price).toLocaleString() : "—";

  if (priceEl) {
    priceEl.classList.add("changing");
    setTimeout(function () {
      priceEl.textContent = formatted;
      priceEl.classList.remove("changing");
    }, 280);
  }
  if (stickyPriceEl && price) {
    stickyPriceEl.textContent = formatted;
  }
}

function swapVariationImage(imageUrl, altText) {
  const fakeThumb = { dataset: { src: imageUrl, alt: altText } };
  switchImage(fakeThumb);
  document.querySelectorAll(".pd-thumb").forEach(function (t) {
    t.classList.remove("active");
  });
}

function updateCtaStock(inStock) {
  const ctaBtn = document.getElementById("pd-add-to-cart");
  const stickyCta = document.getElementById("pd-sticky-cta");

  if (ctaBtn) {
    ctaBtn.disabled = !inStock;
    ctaBtn.classList.toggle("disabled", !inStock);
    ctaBtn.textContent = inStock ? "Add to Cart" : "Unavailable";
  }
  if (stickyCta) {
    stickyCta.disabled = !inStock;
    stickyCta.textContent = inStock ? "Add to Cart" : "Unavailable";
  }
}

// QUANTITY STEPPER
function adjustQty(delta) {
  const input = document.getElementById("pd-qty");
  if (!input) return;
  input.value = Math.min(99, Math.max(1, parseInt(input.value) + delta));
}

// STICKY BAR
function initStickyBar() {
  const ctaRow = document.querySelector(".pd-cta-row");
  const stickyBar = document.getElementById("pd-sticky-bar");
  if (!ctaRow || !stickyBar) return;

  const obs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) {
        stickyBar.classList.toggle("visible", !e.isIntersecting);
      });
    },
    { threshold: 0 },
  );

  obs.observe(ctaRow);
}

// TABS
function switchTab(btn, panelId) {
  document.querySelectorAll(".pd-tab-btn").forEach(function (b) {
    b.classList.remove("active");
    b.setAttribute("aria-selected", "false");
  });
  document.querySelectorAll(".pd-tab-panel").forEach(function (p) {
    p.classList.remove("active");
  });

  btn.classList.add("active");
  btn.setAttribute("aria-selected", "true");

  const panel = document.getElementById(panelId);
  if (panel) panel.classList.add("active");
}

// SHARE

function openModal(modalId) {
  modalId = modalId || "pd-modal";
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
  }
}

function closeModal(modalId) {
  modalId = modalId || "pd-modal";
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("open");
    document.body.style.overflow = "";
  }
}

function initEscapeKey() {
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });
}

// QUOTE FORM — AJAX SUBMIT

function clearFormErrors(form) {
  form.querySelectorAll(".pd-field-error").forEach(function (el) {
    el.classList.remove("visible");
  });
  form
    .querySelectorAll(".pd-field-input, .pd-field-textarea")
    .forEach(function (el) {
      el.classList.remove("error");
    });
}

function setFormSubmitting(isSubmitting) {
  const submitBtn = document.getElementById("pd-quote-submit");
  const label = document.getElementById("pd-submit-label");
  const spinner = document.getElementById("pd-submit-spinner");

  if (!submitBtn) return;
  submitBtn.disabled = isSubmitting;
  label.style.display = isSubmitting ? "none" : "inline";
  spinner.style.display = isSubmitting ? "inline" : "none";
}

function showFormErrors(form, errors) {
  Object.keys(errors).forEach(function (field) {
    const input = form.querySelector("[name='" + field + "']");
    const errEl = document.getElementById("q-" + field + "-err");
    if (input) input.classList.add("error");
    if (errEl) {
      errEl.textContent = errors[field];
      errEl.classList.add("visible");
    }
  });
}

function showModalSuccess() {
  const formWrap = document.getElementById("pd-modal-form-wrap");
  const success = document.getElementById("pd-modal-success");
  if (formWrap) formWrap.style.display = "none";
  if (success) success.classList.add("visible");
}

function handleQuoteSubmit(e, PD) {
  e.preventDefault();
  const form = e.currentTarget;

  clearFormErrors(form);
  setFormSubmitting(true);

  fetch(PD.quoteUrl, {
    method: "POST",
    headers: { "X-Requested-With": "XMLHttpRequest" },
    body: new FormData(form),
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (json) {
      if (json.ok) {
        showModalSuccess();
      } else {
        showFormErrors(form, json.errors || {});
        setFormSubmitting(false);
      }
    })
    .catch(function () {
      setFormSubmitting(false);
    });
}

function initQuoteForm(PD, modalId) {
  modalId = modalId || "pd-modal";
  const form = document.getElementById(modalId + "-form");
  if (form)
    form.addEventListener("submit", function (e) {
      handleQuoteSubmit(e, PD);
    });
}

/* ─────────────────────────────────────────────
 * EXPOSE GLOBALS (called from inline HTML attrs)
 * ───────────────────────────────────────────── */

function exposeGlobals() {
  window.pdSwitchImage = switchImage;
  window.pdSelectVariation = selectVariation;
  window.pdQty = adjustQty;
  window.pdTab = switchTab;
  window.pdOpenModal = openModal;
  window.pdCloseModal = closeModal;
  window.pdCloseModalOutside = function (e, modalId) {
    if (e.target === document.getElementById(modalId || "pd-modal")) {
      closeModal(modalId);
    }
  };
  window.closeModal = closeModal;
}

/* ─────────────────────────────────────────────
 * MAIN
 * ───────────────────────────────────────────── */

function main(PD) {
  exposeGlobals(PD);
  window.pdShare = function () {
    const toast = document.getElementById("pd-share-toast");

    if (navigator.share) {
      navigator
        .share({ title: PD.productName, url: window.location.href })
        .catch(function () {});
    } else {
      navigator.clipboard.writeText(window.location.href).then(function () {
        if (toast) {
          toast.classList.add("visible");
          setTimeout(function () {
            toast.classList.remove("visible");
          }, 2400);
        }
      });
    }
  };

  initStickyBar();
  initEscapeKey();
  initQuoteForm(PD);
}
