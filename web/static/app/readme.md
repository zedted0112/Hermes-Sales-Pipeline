# Web app (frontend)

Sales pipeline UI served at `/app`. Full project documentation is in the **[root README](../../../README.md)**.

## Files

- `index.html` — shell, hero, workflow, pipeline workspace
- `index.js` — guided/explorer modes, API calls, live agent log
- `css/index.css` — pipeline inputs, agent panel, step cards

## Tailwind

Classes use the `tw-` prefix. Production build: `css/tailwind-build.css`.

After JS/CSS changes, bump cache-bust query strings in `index.html` (`?v=` on `index.css` and `index.js`).
