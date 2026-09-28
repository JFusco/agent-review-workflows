export default {
  "*.py": "node scripts/python.cjs -m ruff check --fix",
  "*.{cjs,js,mjs}": "eslint --fix --max-warnings=0 --no-warn-ignored"
};
