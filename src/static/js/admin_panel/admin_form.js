document.addEventListener("DOMContentLoaded", function () {
  function togglePerms(isSuperadmin) {
    const section = document.getElementById("perms-section");
    if (!section) return;
    section.style.opacity = isSuperadmin ? "0.4" : "1";
    section.style.pointerEvents = isSuperadmin ? "none" : "auto";
  }

  const superadminCheckbox = document.getElementById("is-superadmin");
  if (superadminCheckbox) {
    superadminCheckbox.addEventListener("change", function () {
      togglePerms(this.checked);
    });
    togglePerms(superadminCheckbox.checked);
  }
});
