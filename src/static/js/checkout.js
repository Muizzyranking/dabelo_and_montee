(function () {
  "use strict";

  const form = document.getElementById("checkout-form");
  if (!form) return;

  const payBtn = document.getElementById("pay-btn");
  const btnLabel = document.getElementById("pay-btn-label");
  const btnSpinner = document.getElementById("pay-btn-spinner");
  const errBox = document.getElementById("checkout-errors");

  const PAY_URL = form.dataset.payUrl;
  const VERIFY_URL = form.dataset.verifyUrl;
  const ADDRESS_URL = form.dataset.addressUrl;

  function setLoading(on) {
    payBtn.disabled = on;
    btnLabel.classList.toggle("hidden", on);
    btnSpinner.classList.toggle("hidden", !on);
  }

  function clearErrors() {
    errBox.classList.add("hidden");
    errBox.textContent = "";
    form.querySelectorAll('[id^="err-"]').forEach(function (el) {
      el.classList.add("hidden");
      el.textContent = "";
    });
    form.querySelectorAll("input, textarea").forEach(function (el) {
      el.classList.remove("border-red-400");
    });
  }

  function showErrors(errors) {
    if (errors && typeof errors === "object" && !Array.isArray(errors)) {
      Object.keys(errors).forEach(function (field) {
        var errEl = document.getElementById("err-" + field);
        var input = form.querySelector('[name="' + field + '"]');
        if (errEl) {
          errEl.textContent = errors[field];
          errEl.classList.remove("hidden");
        }
        if (input) {
          input.classList.add("border-red-400");
        }
      });
    } else {
      errBox.textContent = errors || "Something went wrong. Please try again.";
      errBox.classList.remove("hidden");
    }
  }

  function saveAddressToAccount(formData) {
    if (!ADDRESS_URL) return;

    var addressData = new FormData();
    addressData.append("address_line_1", formData.get("address_line_1") || "");
    addressData.append("address_line_2", formData.get("address_line_2") || "");
    addressData.append("city", formData.get("city") || "");
    addressData.append("state", formData.get("state") || "");
    addressData.append(
      "csrfmiddlewaretoken",
      formData.get("csrfmiddlewaretoken"),
    );

    fetch(ADDRESS_URL, { method: "POST", body: addressData }).catch(
      function () {
        // Intentionally silent — saving address is a convenience, not critical
      },
    );
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearErrors();
    setLoading(true);

    var formData = new FormData(form);

    fetch(PAY_URL, {
      method: "POST",
      headers: { "X-Requested-With": "XMLHttpRequest" },
      body: formData,
    })
      .then(function (r) {
        if (!r.ok && r.status !== 400) {
          // Unexpected server error (500 etc.)
          throw new Error("server_error");
        }
        return r.json();
      })
      .then(function (res) {
        if (!res.ok) {
          setLoading(false);
          showErrors(res.errors || res.message);
          return;
        }

        var saveCheckbox = form.querySelector("#co-save");
        if (saveCheckbox && saveCheckbox.checked) {
          saveAddressToAccount(formData);
        }

        setLoading(false);
        openPaystackPopup(res);
      })
      .catch(function () {
        setLoading(false);
        showErrors("Something went wrong. Please try again.");
      });
  });

  function openPaystackPopup(res) {
    var handler = new PaystackPop();

    handler.newTransaction({
      key: res.key,
      email: res.email,
      amount: res.amount,
      ref: res.reference,
      currency: "NGN",

      onSuccess: function (transaction) {
        setLoading(true);
        btnLabel.textContent = "Verifying payment\u2026";
        window.location.href =
          VERIFY_URL + "?reference=" + transaction.reference;
      },

      onCancel: function () {
        setLoading(false);
        showErrors("Payment was cancelled. You can try again.");
      },
    });

    setTimeout(function () {
      setLoading(false);
    }, 10000);
  }
})();
