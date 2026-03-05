function floatingCart() {
  function applyCartBtnBrand() {
    const btn = document.getElementById("cart-float-btn");
    const badge = document.getElementById("cart-count-badge");
    if (!btn || !badge) return;

    const hasDabelo = !!document.querySelector(
      '.shop-dabelo, .pd-dabelo, [data-brand="dabelo"]',
    );
    const hasMontee = !!document.querySelector(
      '.shop-montee, .pd-montee, [data-brand="montee"]',
    );

    if (hasDabelo) {
      btn.style.background = "#0F4D2F";
      badge.style.background = "#C59A3D";
    } else if (hasMontee) {
      btn.style.background = "#563772";
      badge.style.background = "#E84C9A";
    } else {
      btn.style.background =
        "linear-gradient(135deg, #0F4D2F 0%, #563772 100%)";
      badge.style.background = "#C59A3D";
    }
  }
  document.addEventListener("DOMContentLoaded", applyCartBtnBrand);
}

/* ─── CART COUNT ─── */
function updateCartCount(count) {
  const badge = document.getElementById("cart-count-badge");
  const drawerCount = document.getElementById("drawer-item-count");
  const drawerPlural = document.getElementById("drawer-item-plural");

  if (badge) {
    badge.textContent = count;
    // Pulse animation
    badge.classList.add("scale-125");
    setTimeout(function () {
      badge.classList.remove("scale-125");
    }, 200);
  }
  if (drawerCount) drawerCount.textContent = count;
  if (drawerPlural) drawerPlural.textContent = count === 1 ? "" : "s";
}

// Fetch count on page load
document.addEventListener("DOMContentLoaded", function () {
  fetch("/cart/count/")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      updateCartCount(data.count);
    })
    .catch(function () {});
});

/* ─── CART DRAWER ─── */
function cartDrawerOpen() {
  const drawer = document.getElementById("cart-drawer");
  const backdrop = document.getElementById("cart-drawer-backdrop");
  const body = document.getElementById("cart-drawer-body");

  if (!drawer) return;

  // Show backdrop + drawer
  backdrop.classList.remove("opacity-0", "pointer-events-none");
  backdrop.classList.add("opacity-100");
  drawer.classList.remove("translate-x-full");
  document.body.style.overflow = "hidden";

  // Load drawer content
  body.innerHTML = `
    <div class="flex items-center justify-center h-40 text-warm-gray text-sm">
      Loading…
    </div>
  `;

  fetch("/cart/drawer/")
    .then(function (r) {
      return r.text();
    })
    .then(function (html) {
      body.innerHTML = html;
      bindDrawerActions();
    })
    .catch(function () {
      body.innerHTML = `
        <div class="flex items-center justify-center h-40 text-warm-gray text-sm">
          Could not load cart. Please try again.
        </div>
      `;
    });
}

function cartDrawerClose() {
  const drawer = document.getElementById("cart-drawer");
  const backdrop = document.getElementById("cart-drawer-backdrop");
  if (!drawer) return;

  drawer.classList.add("translate-x-full");
  backdrop.classList.add("opacity-0", "pointer-events-none");
  backdrop.classList.remove("opacity-100");
  document.body.style.overflow = "";
}

function cartDrawerRefresh() {
  const body = document.getElementById("cart-drawer-body");
  if (!body) return;

  fetch("/cart/drawer/")
    .then(function (r) {
      return r.text();
    })
    .then(function (html) {
      body.innerHTML = html;
      bindDrawerActions();
    });
}

/* ─── DRAWER ACTION BINDING ─── */
function bindDrawerActions() {
  document.querySelectorAll("[data-drawer-decrease]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const itemId = btn.dataset.drawerDecrease;
      const input = document.querySelector(`[data-drawer-qty="${itemId}"]`);
      const current = parseInt(input ? input.value : 1);
      cartUpdateItem(itemId, current - 1);
    });
  });

  // Quantity increase
  document.querySelectorAll("[data-drawer-increase]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const itemId = btn.dataset.drawerIncrease;
      const input = document.querySelector(`[data-drawer-qty="${itemId}"]`);
      const current = parseInt(input ? input.value : 1);
      cartUpdateItem(itemId, current + 1);
    });
  });

  // Remove
  document.querySelectorAll("[data-drawer-remove]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      cartRemoveItem(btn.dataset.drawerRemove);
    });
  });
}

/* ─── ADD TO CART ─── */
function cartAdd(productId, variationId, quantity) {
  const formData = new FormData();
  formData.append("product_id", productId);
  formData.append("quantity", quantity || 1);
  if (variationId) formData.append("variation_id", variationId);
  formData.append("csrfmiddlewaretoken", getCsrf());

  fetch("/cart/add/", {
    method: "POST",
    body: formData,
  })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (data.ok) {
        showToast(data.message, "success");
        updateCartCount(data.cart_count);
      } else {
        showToast(data.message, "error");
      }
    })
    .catch(function () {
      showToast("Something went wrong. Please try again.", "error");
    });
}

/* ─── UPDATE QUANTITY ─── */
function cartUpdateItem(itemId, quantity) {
  const formData = new FormData();
  formData.append("item_id", itemId);
  formData.append("quantity", quantity);
  formData.append("csrfmiddlewaretoken", getCsrf());

  fetch("/cart/update/", { method: "POST", body: formData })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (data.ok) {
        updateCartCount(data.cart_count);
        updateDrawerSubtotal(data.subtotal);
        if (data.removed) {
          cartDrawerRefresh();
        } else {
          const input = document.querySelector(`[data-drawer-qty="${itemId}"]`);
          if (input) input.value = quantity;
          const lineEl = document.querySelector(
            `[data-drawer-line="${itemId}"]`,
          );
          if (lineEl) {
            fetch("/cart/drawer/")
              .then(function (r) {
                return r.text();
              })
              .then(function (html) {
                document.getElementById("cart-drawer-body").innerHTML = html;
                bindDrawerActions();
              });
          }
        }
      }
    });
}

/* ─── REMOVE ITEM ─── */
function cartRemoveItem(itemId) {
  const formData = new FormData();
  formData.append("item_id", itemId);
  formData.append("csrfmiddlewaretoken", getCsrf());

  fetch("/cart/remove/", { method: "POST", body: formData })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (data.ok) {
        updateCartCount(data.cart_count);
        updateDrawerSubtotal(data.subtotal);
        cartDrawerRefresh();
        showToast("Item removed from cart.", "info");
      }
    });
}

/* ─── DRAWER SUBTOTAL UPDATE ─── */
function updateDrawerSubtotal(subtotal) {
  const el = document.getElementById("drawer-subtotal");
  if (el) {
    const formatted = "₦" + parseInt(subtotal).toLocaleString();
    el.textContent = formatted;
  }
}

function getCsrf() {
  const cookie = document.cookie.split(";").find(function (c) {
    return c.trim().startsWith("csrftoken=");
  });
  return cookie ? cookie.trim().split("=")[1] : "";
}

function main() {
  floatingCart();
}

main();
