"use strict";

const js = require("@eslint/js");
const globals = require("globals");

module.exports = [
  {
    ignores: [
      "node_modules/**",
      ".pnpm-store/**",
      ".venv/**",
      ".husky/_/**",
      "scripts/wiki/**"
    ]
  },
  js.configs.recommended,
  { rules: { "no-unused-vars": ["error", { ignoreRestSiblings: true }] } },
  {
    files: ["**/*.cjs"],
    languageOptions: { sourceType: "commonjs", globals: globals.node }
  },
  {
    files: ["**/*.{js,mjs}"],
    languageOptions: { sourceType: "module", globals: globals.node }
  }
];
