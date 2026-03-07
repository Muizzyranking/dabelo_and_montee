(function () {
  "use strict";

  const list = document.getElementById("cart-items-list");
  if (!list) return;

  const UPDATE_URL = list.dataset.updateUrl;
  const COUNT_URL = list.dataset.countUrl;

  function getLiveQty(itemId) {
    var el = document.getElementById("cart-page-qty-" + itemId);
    return el ? parseInt(el.textContent, 10) || 0 : 0;
  }

  window.cartPageIncrease = function (itemId) {
    cartPageUpdate(itemId, getLiveQty(itemId) + 1);
  };

  window.cartPageDecrease = function (itemId) {
    cartPageUpdate(itemId, getLiveQty(itemId) - 1);
  };

  window.cartPageRemove = function (itemId) {
    cartPageUpdate(itemId, 0);
  };

  function cartPageUpdate(itemId, quantity) {
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
          // Update qty span with the confirmed new quantity
          var qtyEl = document.getElementById("cart-page-qty-" + itemId);
          if (qtyEl) qtyEl.textContent = quantity;
          refreshSubtotal();
        }
      })
      .catch(function () {});
  }

  function removeItemRow(itemId, cartCount) {
    var el = document.getElementById("cart-page-item-" + itemId);
    if (!el) return;

    el.style.transition = "opacity 0.25s ease, transform 0.25s ease";
    el.style.opacity = "0";
    el.style.transform = "translateX(-8px)";

    setTimeout(function () {
      el.remove();
      if (cartCount === 0) location.reload();
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
