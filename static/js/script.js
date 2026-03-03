function initScrollReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-fade-up");
          entry.target.style.opacity = "1";
        }
      });
    },
    { threshold: 0.1 },
  );

  document.querySelectorAll(".reveal").forEach((el) => {
    el.style.opacity = "0";
    observer.observe(el);
  });
}

function initRevealObserver() {
  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 },
  );

  document.querySelectorAll(".reveal").forEach((el) => {
    observer.observe(el);
  });
}

function initNavbarScroll() {
  const nav = document.getElementById("brand-nav");
  if (!nav) return;
  const brand = nav.dataset.brand;

  function onScroll() {
    if (window.scrollY > 60) {
      if (brand === "dabelo") {
        nav.classList.add("bg-dabelo-green", "shadow-warm-md");
        nav.classList.remove("bg-transparent");
      } else {
        nav.classList.add("bg-motee-purple", "shadow-purple-glow");
        nav.classList.remove("bg-transparent");
      }
    } else {
      nav.classList.remove(
        "bg-dabelo-green",
        "shadow-warm-md",
        "bg-motee-purple",
        "shadow-purple-glow",
      );
      nav.classList.add("bg-transparent");
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

function animateHamburger(btn, isOpen) {
  const lines = btn.querySelectorAll(".dab-line");
  if (!isOpen) {
    lines[0].style.transform = "translateY(6px) rotate(45deg)";
    lines[1].style.opacity = "0";
    lines[2].style.transform = "translateY(-6px) rotate(-45deg)";
  } else {
    lines.forEach((line) => {
      line.style.transform = "";
      line.style.opacity = "";
    });
  }
}

function initMobileMenu() {
  const btn = document.getElementById("brand-menu-btn");
  const menu = document.getElementById("brand-mobile-menu");

  if (!btn || !menu) return;

  btn.addEventListener("click", () => {
    const isOpen = !menu.classList.contains("hidden");

    menu.classList.toggle("hidden", isOpen);
    menu.classList.toggle("flex", !isOpen);
    btn.setAttribute("aria-expanded", String(!isOpen));
    animateHamburger(btn, isOpen);
  });

  document.addEventListener("click", (e) => {
    if (!btn.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.add("hidden");
      menu.classList.remove("flex");
      btn.setAttribute("aria-expanded", "false");

      const lines = btn.querySelectorAll(".dab-line");
      lines.forEach((line) => {
        line.style.transform = "";
        line.style.opacity = "";
      });
    }
  });
}

function jointMobileMenu() {
  const btn = document.getElementById("hamburger-btn");
  const menu = document.getElementById("mobile-menu");
  if (!btn || !menu) return;

  btn.addEventListener("click", function () {
    const isOpen = menu.classList.contains("open");
    menu.classList.toggle("open", !isOpen);
    btn.setAttribute("aria-expanded", String(!isOpen));

    animateHamburger(btn, isOpen);
  });

  document.addEventListener("click", function (e) {
    if (!btn.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
      const lines = btn.querySelectorAll(".dab-line");
      lines.forEach((line) => {
        line.style.transform = "";
        line.style.opacity = "";
      });
    }
  });
}

function main() {
  initScrollReveal();
  initRevealObserver();
  initNavbarScroll();
  initMobileMenu();
  jointMobileMenu();
}

main();
