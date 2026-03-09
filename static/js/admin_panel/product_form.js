document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("product-form");
  const csrfToken = form ? form.dataset.csrf : "";
  const productPk = form ? form.dataset.productPk : "";
  const primaryDeleteUrl = form ? form.dataset.primaryDeleteUrl : "";
  const galleryDeleteUrl = form ? form.dataset.galleryDeleteUrl : "";
  const varDeleteBase = form ? form.dataset.variationDeleteUrl : "";

  let newVarIdx = 0;
  let newAttrIdx = 0;

  // ── Brand card selection ──────────────────────────────────────────
  function activateBrandCard(value) {
    document.querySelectorAll(".brand-card").forEach(function (card) {
      const selected = card.dataset.brand === value;
      card.style.borderColor = selected ? "var(--ap-gold)" : "var(--ap-border)";
      card.style.backgroundColor = selected
        ? "rgba(197,154,61,0.08)"
        : "transparent";
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

  // ── Product type toggle ───────────────────────────────────────────
  function toggleType(type) {
    const varSection = document.getElementById("variations-section");
    const priceField = document.getElementById("price-field");
    if (!varSection || !priceField) return;
    if (type === "variable") {
      varSection.style.display = "block";
      priceField.style.display = "none";
    } else {
      varSection.style.display = "none";
      priceField.style.display = "block";
    }
  }

  const typeSelect = document.getElementById("f-type");
  if (typeSelect) {
    typeSelect.addEventListener("change", function () {
      toggleType(this.value);
    });
    toggleType(typeSelect.value);
  }

  // ── Add variation row ─────────────────────────────────────────────
  window.addVariation = function () {
    const list = document.getElementById("new-variations-list");
    const idx = "new_" + newVarIdx++;
    const row = document.createElement("div");
    row.className = "var-row";
    row.id = "new-var-" + idx;
    row.innerHTML = `
      <input type="text"   name="new_var_name_${idx}"  class="ap-input" placeholder="e.g. Large (serves 40)" />
      <input type="number" name="new_var_price_${idx}" class="ap-input" placeholder="Price" min="0" />
      <input type="file"   name="new_var_image_${idx}" class="ap-input" style="padding:4px;font-size:0.72rem" accept="image/*" />
      <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
        <input type="checkbox" name="new_var_stock_${idx}" checked
               style="accent-color:var(--ap-gold);width:16px;height:16px" />
      </label>
      <button type="button"
              onclick="this.closest('.var-row').remove()"
              class="ap-btn ap-btn-danger ap-btn-sm"
              style="padding:6px 8px">✕</button>
    `;
    list.appendChild(row);
  };

  // ── Delete existing variation via AJAX ────────────────────────────
  window.deleteVariation = function (pk) {
    if (!confirm("Delete this variation?")) return;
    const url = varDeleteBase.replace("0", pk); // template sets base url with placeholder 0
    post(url).then(function (data) {
      if (data.ok) {
        const row = document.getElementById("var-row-" + pk);
        if (row) row.remove();
      }
    });
  };

  // ── Add attribute row ─────────────────────────────────────────────
  window.addAttribute = function () {
    const list = document.getElementById("new-attributes-list");
    const idx = "new_" + newAttrIdx++;
    const row = document.createElement("div");
    row.className = "attr-row";
    row.innerHTML = `
      <input type="text" name="new_attr_name_${idx}"  class="ap-input" placeholder="e.g. Weight" />
      <input type="text" name="new_attr_value_${idx}" class="ap-input" placeholder="e.g. 2kg" />
      <button type="button"
              onclick="this.closest('.attr-row').remove()"
              class="ap-btn ap-btn-danger ap-btn-sm"
              style="padding:6px 8px">✕</button>
    `;
    list.appendChild(row);
  };

  // ── Primary image preview ─────────────────────────────────────────
  const primaryInput = document.querySelector('input[name="primary_image"]');
  if (primaryInput) {
    primaryInput.addEventListener("change", function () {
      const wrap = document.getElementById("primary-preview");
      const img = document.getElementById("primary-preview-img");
      if (!wrap || !img || !this.files || !this.files[0]) return;
      const reader = new FileReader();
      reader.onload = function (e) {
        img.src = e.target.result;
        wrap.style.display = "block";
      };
      reader.readAsDataURL(this.files[0]);
    });
  }

  // ── Delete primary image via AJAX ─────────────────────────────────
  window.deletePrimaryImage = function () {
    if (!confirm("Remove the primary image?")) return;
    post(primaryDeleteUrl).then(function (data) {
      if (data.ok) {
        const wrap = document.getElementById("primary-img-wrap");
        if (wrap) wrap.remove();
      }
    });
  };

  // ── Preview new gallery images ────────────────────────────────────
  const galleryInput = document.querySelector('input[name="gallery_images"]');
  if (galleryInput) {
    galleryInput.addEventListener("change", function () {
      const container = document.getElementById("gallery-preview");
      if (!container) return;
      container.innerHTML = "";
      Array.from(this.files).forEach(function (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const div = document.createElement("div");
          div.className = "img-card";
          div.innerHTML = `
            <img src="${e.target.result}" alt="Preview" />
            <div style="position:absolute;bottom:0;left:0;right:0;
                        background:rgba(197,154,61,0.9);
                        font-size:0.55rem;font-weight:700;
                        letter-spacing:0.1em;text-transform:uppercase;
                        color:#000;padding:3px 6px;text-align:center">
              New
            </div>
          `;
          container.appendChild(div);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  // ── Delete gallery image via AJAX ─────────────────────────────────
  window.deleteGalleryImage = function (entryPk) {
    if (!confirm("Delete this gallery image?")) return;
    const url = galleryDeleteUrl.replace("0", entryPk);
    post(url).then(function (data) {
      if (data.ok) {
        const card = document.getElementById("gallery-entry-" + entryPk);
        if (card) card.remove();
      }
    });
  };

  // ── Auto-generate slug from name ──────────────────────────────────
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

  // ── AJAX helper ───────────────────────────────────────────────────
  function post(url) {
    const fd = new FormData();
    fd.append("csrfmiddlewaretoken", csrfToken);
    return fetch(url, { method: "POST", body: fd }).then(function (r) {
      return r.json();
    });
  }
});
