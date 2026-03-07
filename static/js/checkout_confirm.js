
(function () {
  "use strict";

  const list = document.getElementById("cart-items-list");
  if (!list) return; // guard: only run on cart page

  const UPDATE_URL = list.dataset.updateUrl;
  const COUNT_URL = list.dataset.countUrl;

  window.cartPageUpdate = function (itemId, quantity) {
    var formData = new FormData();
    formData.append("item_id", itemId);
    formData.append("quantity", quantity);
    formData.append("csrfmiddlewaretoken", getCsrf());

    fetch(UPDATE_URL, { method: "POST", body: formData })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (!data.ok) return;

        updateCartCount(data.cart_count);

        if (data.removed) {
          removeItemRow(itemId, data.cart_count);
        } else {
          var qtyEl = document.getElementById("cart-page-qty-" + itemId);
          if (qtyEl) qtyEl.textContent = quantity;
          refreshSubtotal();
        }
      })
      .catch(function () {
        // Silent — the user can retry by clicking again
      });
  };

  window.cartPageRemove = function (itemId) {
    window.cartPageUpdate(itemId, 0);
  };

  // ------------------------------------------------------------------ //
  // Private helpers
  // ------------------------------------------------------------------ //

  function removeItemRow(itemId, cartCount) {
    var el = document.getElementById("cart-page-item-" + itemId);
    if (!el) return;

    el.style.transition = "opacity 0.25s ease, transform 0.25s ease";
    el.style.opacity = "0";
    el.style.transform = "translateX(-8px)";

    setTimeout(function () {
      el.remove();
      if (cartCount === 0) {
        location.reload();
      }
    }, 250);
  }

  function refreshSubtotal() {
    fetch(COUNT_URL)
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        updateCartCount(data.count);
      })
      .catch(function () {});
  }
})();
