document.addEventListener("DOMContentLoaded", function () {

  // ── Brand card selection ──────────────────────────────────────────
  function activateBrandCard(value) {
    document.querySelectorAll(".brand-card").forEach(function (card) {
      const isSelected = card.dataset.brand === value;
      card.style.borderColor     = isSelected ? "var(--ap-gold)" : "var(--ap-border)";
      card.style.backgroundColor = isSelected ? "rgba(197,154,61,0.08)" : "transparent";
    });
  }

  document.querySelectorAll(".brand-radio").forEach(function (radio) {
    radio.addEventListener("change", function () {
      activateBrandCard(radio.value);
    });
    if (radio.checked) activateBrandCard(radio.value);
  });

  document.querySelectorAll(".brand-card").forEach(function (card) {
    card.addEventListener("click", function () {
      const radio = document.getElementById("brand-" + card.dataset.brand);
      if (radio) {
        radio.checked = true;
        radio.dispatchEvent(new Event("change"));
      }
    });
  });

  // ── Auto-generate slug from name ─────────────────────────────────
  const nameField = document.getElementById("f-name");
  const slugField = document.getElementById("f-slug");

  if (nameField && slugField) {
    nameField.addEventListener("input", function () {
      if (!slugField.dataset.manual) {
        slugField.value = nameField.value
          .toLowerCase()
          .replace(/[^a-z0-9\s-]/g, "")
          .replace(/\s+/g, "-")
          .replace(/-+/g, "-");
      }
    });

    slugField.addEventListener("input", function () {
      slugField.dataset.manual = "true";
    });
  }

});
