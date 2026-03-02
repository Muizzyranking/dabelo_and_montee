/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./core/templates/**/*.html",
    "./products/templates/**/*.html",
    "./orders/templates/**/*.html",
    "./accounts/templates/**/*.html",
    "./dashboard/templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        // ── Motee Cakes ───────────────────────────────
        "motee-pink":    "#E84C9A",
        "motee-purple":  "#7A4FA3",
        "motee-blue":    "#1EB1E7",
        // ── Dabelo Café ───────────────────────────────
        "dabelo-green":  "#0F4D2F",
        "dabelo-gold":   "#C59A3D",
        "dabelo-leaf":   "#7FAF3A",
      },
      fontFamily: {
        // Joint / neutral
        "display": ["'Playfair Display'", "Georgia", "serif"],
        "body":    ["'DM Sans'", "sans-serif"],
        // Motee Cakes — playful elegance
        "motee-display": ["'Cormorant Garamond'", "Georgia", "serif"],
        "motee-body":    ["'Nunito'", "sans-serif"],
        // Dabelo Café — earthy, premium
        "dabelo-display": ["'Fraunces'", "Georgia", "serif"],
        "dabelo-body":    ["'Karla'", "sans-serif"],
      },
      backgroundImage: {
        "motee-gradient": "linear-gradient(135deg, #E84C9A 0%, #7A4FA3 100%)",
        "dabelo-gradient": "linear-gradient(135deg, #0F4D2F 0%, #7FAF3A 100%)",
      },
      animation: {
        "fade-up":   "fadeUp 0.6s ease forwards",
        "fade-in":   "fadeIn 0.4s ease forwards",
        "float":     "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":      { transform: "translateY(-12px)" },
        },
      },
    },
  },
  plugins: [],
}
