# Frontend Changes: Dark/Light Theme Toggle

## Summary
Added a toggle button that lets users switch between the existing dark theme and a new light theme, with the preference persisted across visits.

## Files Changed

### `frontend/index.html`
- Added a `#themeToggle` button (fixed, top-right of the viewport, outside `.container` so it stays visible regardless of page content) containing inline SVG sun and moon icons.
- Button includes `aria-label`, `aria-pressed`, and `title` attributes for accessibility; it's a native `<button>` so it's keyboard-focusable and activates on Enter/Space by default.
- Bumped cache-busting query params for `style.css` and `script.js` from `v=9` to `v=10`.

### `frontend/style.css`
- Added a `:root[data-theme="light"]` block that overrides all existing CSS custom properties (`--background`, `--surface`, `--surface-hover`, `--text-primary`, `--text-secondary`, `--border-color`, `--user-message`, `--assistant-message`, `--shadow`, `--focus-ring`, `--welcome-bg`, `--welcome-border`) with a light palette that keeps AA-level contrast (e.g. `--text-primary: #0f172a` on `--background: #ffffff`, `--text-secondary: #475569`).
- Added a shared transition rule (`background-color`, `color`, `border-color`, 0.3s ease) across the main color-bearing containers (body, sidebar, chat area, message bubbles, stat items, etc.) so switching themes animates smoothly instead of snapping.
- Added `.theme-toggle` styles: a fixed circular button in the top-right corner using the existing surface/border/focus-ring variables so it matches the current design language, with hover/active/focus-visible states consistent with `#sendButton` and `.suggested-item`.
- Added icon-crossfade styles for `.theme-icon-sun` / `.theme-icon-moon` using `opacity`, `rotate`, and `scale` transitions so the sun and moon icons rotate/fade into each other when the theme changes.
- Added a small-screen rule (inside the existing `max-width: 768px` media query) to shrink the toggle button on mobile.

### `frontend/script.js`
- Added `themeToggle` to the cached DOM elements.
- Added `initializeTheme()`, called on load: reads `localStorage.getItem('theme')`, falling back to the `prefers-color-scheme: light` media query, then applies the resolved theme.
- Added `toggleTheme()`: flips between `'light'` and `'dark'` based on the current `data-theme` attribute.
- Added `applyTheme(theme)`: sets/removes `data-theme="light"` on `document.documentElement`, persists the choice to `localStorage`, and updates the toggle button's `aria-pressed`/`aria-label` to reflect the new state.
- Wired the toggle button's `click` listener in `setupEventListeners()`.

## Behavior
- Default/unset theme is the existing dark theme (no `data-theme` attribute).
- Clicking the button (or activating it via keyboard) toggles `data-theme="light"` on `<html>`, switching all CSS variables and animating the transition.
- Theme choice is remembered via `localStorage` and re-applied on next visit; if nothing is saved yet, the OS-level light/dark preference is used.

## Testing Notes
- Verified `script.js` parses with `node --check` and that `index.html` contains the new toggle markup.
- Served the frontend statically and confirmed `index.html`, `style.css`, and `script.js` all return HTTP 200.
- No browser automation tool was available in this environment, so the actual visual rendering/animation was not verified in a live browser — worth a manual spot-check (toggle click, icon crossfade, keyboard activation via Tab+Enter/Space, and contrast in light mode) before merging.
