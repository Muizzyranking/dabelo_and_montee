function showToast(message, type) {
  type = type || "success";

  const colors = {
    success: "bg-white border-l-4 border-dabelo-green text-ink",
    error: "bg-white border-l-4 border-red-400 text-ink",
    info: "bg-white border-l-4 border-dabelo-gold text-ink",
    warning: "bg-white border-l-4 border-yellow-400 text-ink",
  };
  const icons = {
    success: "✓",
    error: "✕",
    info: "ℹ",
    warning: "⚠",
  };
  const iconColors = {
    success: "text-dabelo-green",
    error: "text-red-400",
    info: "text-dabelo-gold",
    warning: "text-yellow-500",
  };

  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = [
    "pointer-events-auto",
    "flex items-start gap-3",
    "px-4 py-3.5",
    "rounded-sm shadow-warm-lg",
    "border border-warm-border",
    "text-sm leading-snug",
    "translate-y-4 opacity-0",
    "transition-all duration-300",
    colors[type] || colors.success,
  ].join(" ");

  toast.innerHTML = `
    <span class="text-base font-bold shrink-0 mt-0.5 ${iconColors[type] || iconColors.success}">
      ${icons[type] || icons.success}
    </span>
    <span class="flex-1">${message}</span>
    <button onclick="this.closest('[data-toast]').remove()"
            class="shrink-0 text-warm-gray hover:text-ink transition-colors ml-1 text-base leading-none">
      ✕
    </button>
  `;
  toast.setAttribute("data-toast", "");
  container.appendChild(toast);

  // Animate in
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      toast.classList.remove("translate-y-4", "opacity-0");
    });
  });

  // Auto dismiss after 3s
  const timer = setTimeout(function () {
    dismissToast(toast);
  }, 3000);

  // Cancel auto-dismiss on hover
  toast.addEventListener("mouseenter", function () {
    clearTimeout(timer);
  });
  toast.addEventListener("mouseleave", function () {
    setTimeout(function () {
      dismissToast(toast);
    }, 1500);
  });
}

function dismissToast(toast) {
  if (!toast || !toast.parentNode) return;
  toast.classList.add("opacity-0", "translate-y-2");
  setTimeout(function () {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, 300);
}
