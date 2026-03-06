function toggleSidebar() {
  const obs = new IntersectionObserver(
    function (e) {
      e.forEach(function (el) {
        if (el.isIntersecting) {
          el.target.classList.add("visible");
          obs.unobserve(el.target);
        }
      });
    },
    { threshold: 0.06 },
  );
  document.querySelectorAll(".reveal").forEach(function (el) {
    obs.observe(el);
  });
  const toggle = document.getElementById("sidebar-toggle");
  const body = document.getElementById("sidebar-body");
  if (toggle && body) {
    toggle.addEventListener("click", function () {
      toggle.classList.toggle("open");
      body.classList.toggle("open");
    });
    if (window.innerWidth > 768) body.classList.add("open");
  }
  const sw = document.getElementById("stock-switch");
  const val = document.getElementById("in-stock-val");
  if (sw && val) {
    sw.addEventListener("click", function () {
      const on = sw.classList.toggle("on");
      val.value = on ? "1" : "";
      document.getElementById("shop-form").submit();
    });
  }
  const si = document.querySelector(".shop-search-input");
  if (si) {
    si.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        document.getElementById("shop-form").submit();
      }
    });
  }
}

function main() {
  toggleSidebar();
}

main();
