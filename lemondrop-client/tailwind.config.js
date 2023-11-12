/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/*.{html,js,jsx,tsx,ts}"],
  theme: {
    extend: {},
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "public/**/*.html",
    "public/**/*.js",
    "public/**/*.jsx",
  ],
  "exclude": ["node_modules"],
  plugins: [],
}

