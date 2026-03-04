/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        /* ── Motee Cakes ── */
        "motee-pink":       "#E84C9A",
        "motee-pink-light": "#F27DBB",
        "motee-purple":     "#563772",
        "motee-purple-mid": "#7B5A9E",
        "motee-purple-pale":"#EEE8F5",
        "motee-blue":       "#1EB1E7",

        /* ── Dabelo Café ── */
        "dabelo-green":     "#0F4D2F",
        "dabelo-green-mid": "#1E7248",
        "dabelo-green-pale":"#E4EFE8",
        "dabelo-gold":      "#C59A3D",
        "dabelo-gold-light":"#DDB96A",
        "dabelo-leaf":      "#7FAF3A",

        /* ── Neutrals / Joint ── */
        "ink":              "#111111",
        "ink-2":            "#1a1a1a",
        "ink-3":            "#2E2316",
        "parchment":        "#FAF8F4",
        "warm":             "#F5EFE4",
        "warm-gray":        "#8a8a85",
        "warm-border":      "#E8E0D0",
        "mid-brown":        "#5C4B30",
      },

      fontFamily: {
        /* Dabelo — earthy authority */
        "dabelo-display": ["'Cormorant'", "Georgia", "serif"],
        "dabelo-body":    ["'Outfit'", "sans-serif"],
        /* Motee — romantic elegance */
        "motee-display":  ["'Playfair Display'", "Georgia", "serif"],
        "motee-body":     ["'Jost'", "sans-serif"],
        /* Joint / neutral */
        "display":        ["'Bodoni Moda'", "Georgia", "serif"],
        "body":           ["'Outfit'", "sans-serif"],
        "mono":           ["'DM Mono'", "monospace"],
      },

      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "1rem" }],
        "display-sm": ["clamp(2.5rem, 5vw, 3.5rem)", { lineHeight: "1.05" }],
        "display-md": ["clamp(3rem, 6vw, 5rem)",   { lineHeight: "1.0"  }],
        "display-lg": ["clamp(3.5rem, 8vw, 7rem)",  { lineHeight: "0.95" }],
      },

      spacing: {
        "18":  "4.5rem",
        "22":  "5.5rem",
        "26":  "6.5rem",
        "30":  "7.5rem",
        "34":  "8.5rem",
        "38":  "9.5rem",
        "128": "32rem",
        "144": "36rem",
      },

      borderRadius: {
        "4xl": "2rem",
        "5xl": "2.5rem",
      },

      boxShadow: {
        "warm-sm":  "0 2px 8px rgba(92,75,48,0.08)",
        "warm-md":  "0 8px 30px rgba(92,75,48,0.12)",
        "warm-lg":  "0 20px 60px rgba(92,75,48,0.16)",
        "warm-xl":  "0 32px 80px rgba(92,75,48,0.22)",
        "green-glow":"0 8px 40px rgba(15,77,47,0.25)",
        "purple-glow":"0 8px 40px rgba(86,55,114,0.25)",
      },

      backgroundImage: {
        "gradient-dabelo": "linear-gradient(135deg, #0F4D2F 0%, #1E7248 100%)",
        "gradient-motee":  "linear-gradient(135deg, #563772 0%, #E84C9A 100%)",
        "gradient-joint":  "linear-gradient(135deg, #0F4D2F 0%, #563772 100%)",
        "gradient-warm":   "linear-gradient(180deg, #FAF8F4 0%, #F5EFE4 100%)",
        "noise":           "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\")",
      },

      animation: {
        "fade-up":      "fadeUp 0.75s cubic-bezier(0.16,1,0.3,1) forwards",
        "fade-in":      "fadeIn 0.6s ease forwards",
        "marquee":      "marquee 28s linear infinite",
        "float":        "float 6s ease-in-out infinite",
        "float-slow":   "float 9s ease-in-out infinite",
        "float-medium": "float 7s ease-in-out infinite",
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
        marquee: {
          "0%":   { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%":      { transform: "translateY(-12px)" },
        },
      },

      transitionTimingFunction: {
        "spring": "cubic-bezier(0.16,1,0.3,1)",
      },

      transitionDuration: {
        "400": "400ms",
      },
    },
  },
  plugins: [],
}
