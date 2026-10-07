# Photo site — Step 1: responsive shell

This is a standalone Vite starter for the selected **Cinema Grid / Blue** design. It is intended for your existing Vite/PHP project on StableHost. It has not been deployed.

## 1. Run the shell

Use Node.js 22.12 or later (a current Node LTS release is recommended). Extract the ZIP, open a terminal in `photo-site-shell`, then run:

```sh
npm ci
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

For the design's Japan example, open `http://localhost:5173/#folder=Japan`.
The normal entry page is the root folder and shows its immediate subfolders **and** its own media.

The sample thumbnails are included locally, so the gallery needs no external image service at runtime. They are illustrative stock photographs, not your photo collection. Sample video entries are still images for testing badges and selection; they do not contain playable videos.

## 2. Check the behaviour

Open `http://localhost:5173/?test=1` and expand **Shell test controls** at the bottom.

- Open folders and use breadcrumbs or browser Back/Forward.
- Click the theme button; reload to check that the choice is remembered.
- Click a media tile: a status message confirms selection.
- Use **Reload with cube loader** to see the supplied cube overlay.
- Use **Simulate error**, then **Try again**, to check recovery.
- Open **Family** to check the empty state and bottom-aligned footer.
- Open Japan → Kyoto → An evening walk through the old streets to check long breadcrumbs.
- Resize to 320px, 390px, 768px and desktop width. Mobile uses two columns; folder cards stack.

`?test=1` only exposes development controls. The normal page does not show them.

## 3. Understand the modules

| File | Responsibility |
| --- | --- |
| `src/main.js` | Creates the demo source and controller; supplies temporary media-selection feedback. |
| `src/app/AppController.js` | Folder loading, hash navigation, loading/error handling and selection events. |
| `src/app/GalleryConfig.js` | Loads runtime JSON settings and applies validated CSS variables. |
| `src/app/ThemeController.js` | Applies `:root[data-theme]` and remembers the choice. |
| `src/components/GalleryShell.js` | Header, content regions, status, empty/error states. |
| `src/components/Breadcrumbs.js` | Ancestor navigation. |
| `src/components/FolderGrid.js` | Folder cards and cover fallback. |
| `src/components/MediaGrid.js` | Thumbnail rows, video badges and media selection. |
| `src/components/gallery.scss` | Responsive gallery layout. |
| `src/styles/theme.scss` | Theme variables, base rules and supplied-component integration styles. |
| `src/demo/DemoSource.js` | In-memory folder tree with a short artificial loading delay. |
| `src/demo/DemoControls.js` | Optional manual test controls. |
| `src/shared/` | Your four supplied files, plus DOM/icon helpers. |
| `tests/shell.spec.js` | Repeatable browser tests. |

The original `cubeOverlay.js`, `cubeOverlay.scss`, `footer.js` and `footer.scss` are copied unchanged. Their existing APIs remain:

```js
await gCubeOverlay.start();
await gCubeOverlay.stop();
gFooter.mount(target);
gFooter.setText('© unclecheah');
gFooter.unmount();
```

`public/gallery-config.json` controls layout sizing without rebuilding. `GalleryConfig` loads it once at startup.

`theme.scss` adds `.d-none`, which the overlay previously expected from Bootstrap. It supplies the `--ui-*` variables used by the footer and adds reduced-motion styling. The page uses flex layout so the footer sits at the bottom on short pages and follows content on long pages. It never covers the media.

The supplied exports are singletons: mount one application instance at a time. `AppController.destroy()` removes the shell and navigation listener. An existing application integrating this starter should mount its footer only once.

## 4. Data contract for the next step

The shell depends on one async method:

```js
const folder = await source.getFolder(path);
```

Example return shape:

```js
{
	path: 'Japan',
	name: 'Japan',
	breadcrumbs: [
		{ name: 'Home', path: '' },
		{ name: 'Japan', path: 'Japan' }
	],
	folders: [
		{ name: 'Kyoto', path: 'Japan/Kyoto', cover: '/data/thumbnail/cover.jpg', itemCount: 6 }
	],
	media: [
		{
			id: 'photo-1',
			name: 'Temple.jpg',
			type: 'photo',
			thumbnail: '/data/thumbnail/Temple.jpg',
			width: 1200,
			height: 800
		}
	]
}
```

`itemCount` is optional and, in the demo, counts immediate children plus immediate media. `cover` can be null. `media.type` is `photo` or `video`; video `duration` is an optional display string. Folder paths are relative identifiers; the empty string represents the root. Names are inserted as text, not interpreted as HTML. The real service must supply validated media URLs and safe folder identifiers.

This is the **frontend view model**, not a finalised PHP endpoint or publisher JSON schema. A future API adapter can map the generated indexes into this shape. Full-size media URLs and verified media dimensions will be added for PhotoSwipe.

Media clicks emit a bubbling event from `#app`:

```js
document.querySelector('#app').addEventListener('gallery:media-select', event => {
	const { index, item, items, folderPath } = event.detail;
	// Next step: mediaViewer.open(items, index).
});
```

Replace the temporary status-message listener in `main.js` when integrating the viewer.

## 5. Automated checks

Install Chromium once, then rerun the tests whenever needed:

```sh
npx playwright install chromium --only-shell
npm test
npm run build
```

Tests cover root-folder content, navigation and Back, theme persistence, selection events, video badges, loading/error recovery, empty state, four viewport widths, footer placement, long breadcrumbs, rapid navigation and broken thumbnail fallback.

Playwright starts the Vite server automatically. On a fresh Linux environment, browser system dependencies may also need installation; Windows usually only needs the browser download above.

`npm run build` writes `dist/`. `npm run preview` serves that production build locally. This package is a shell checkpoint, not the finished production gallery.

## 6. Integrating with an existing Vite project

1. Compare your current structure before copying; do not overwrite an existing entry file blindly.
2. Add `jquery` if not already installed and add `sass` as a development dependency.
3. Copy the new `app`, `components`, `demo` and styles files to suitable locations.
4. Point the shared imports to your existing loader/footer files, or use the unchanged copies included here.
5. Mount `AppController` into your existing app container. Keep only one footer and one application instance.
6. Keep the theme import after component imports so its integration rules take precedence.

No Bootstrap package is required by this shell. Vite processes the imported SCSS using Sass.

## Scope of this checkpoint

Implemented: responsive blue/dark and light themes; folder/media shell; hash-based navigation; supplied loader/footer integration; sample data; tests.

Not yet implemented: PHP connection, real folder scanning, generated indexes, PhotoSwipe, video playback, adjacent-photo preloading, local media publisher or upload process.

Next: add the `MediaViewer` wrapper using PhotoSwipe and connect `gallery:media-select`, then replace the demo source with the PHP adapter once the response contract is agreed.

## Reference and demo image sources

- Vite guide: https://vite.dev/guide/
- Vite SCSS support: https://vite.dev/guide/features.html#css-pre-processors
- Demo thumbnails were downloaded from these Unsplash image endpoints at 800px width; retain these references if redistributing the demo assets:
  - https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e
  - https://images.unsplash.com/photo-1540959733332-eab4deabeeaf
  - https://images.unsplash.com/photo-1528360983277-13d401cdc186
  - https://images.unsplash.com/photo-1478436127897-769e1b3f0f36
  - https://images.unsplash.com/photo-1480796927426-f609979314bd
  - https://images.unsplash.com/photo-1492571350019-22de08371fd3

## Verification of this checkpoint

- `npm run build`: passed.
- `npm test`: all 15 tests passed in Chromium, including runtime configuration and independent thumbnail loading.
- Desktop (1440px) and mobile (390px) screenshots visually reviewed.
- Responsive automated checks also covered 320px and 768px.
- Mobile checks used browser viewport emulation, not physical iOS/Android devices.


## Update: favicon, minimum width and thumbnail configuration

### Favicon

Place your own icon at `public/favicon.ico`. Uncomment the favicon line in `index.html`:

```html
<link rel="icon" type="image/x-icon" href="/favicon.ico">
```

The source path is `public/favicon.ico`; the browser URL is `/favicon.ico`. The ICO itself has not been supplied, so this package leaves the link commented out. Vite copies public assets into `dist/` when building.

### Bootstrap

The shell uses custom CSS Grid/Flexbox and jQuery for your supplied components. Bootstrap has not been added. The gallery's variable-width photo rows still need custom styling; Bootstrap could be added later for forms, dropdowns or modals if those features become necessary.

### Runtime configuration

Edit `public/gallery-config.json` during development. After deploying a built site, edit `gallery-config.json` at the deployed site root. Reload the page to apply changes; a Vite rebuild is not needed for this JSON file alone. Rebuilding later copies the source `public/gallery-config.json` again, so keep that source copy in sync with any deployed edits.

```json
{
	"layout": { "minWidth": 320 },
	"thumbnails": {
		"desktopHeight": 220,
		"tabletHeight": 190,
		"mobileColumns": 2,
		"gap": 8,
		"fadeDuration": 180
	}
}
```

| Setting | Meaning |
| --- | --- |
| `minWidth` | Minimum page layout width in CSS pixels. Smaller viewports scroll horizontally; this cannot prevent resizing the browser window. Set 360 if that is your preferred cutoff. |
| `desktopHeight` | Media tile height above 1000px viewport width; widths adapt using media aspect ratios. |
| `tabletHeight` | Media tile height from 601px through 1000px viewport width. |
| `mobileColumns` | Number of equal-width square tile columns at viewport widths up to 600px. Fewer columns means larger thumbnails. |
| `gap` | Space between media tiles in CSS pixels. |
| `fadeDuration` | Per-thumbnail fade duration in milliseconds; use 0 for immediate reveal. |

Folder cover sizes are unchanged. These values control **display size**, not the pixel dimensions or file quality created by the future local thumbnail publisher.

Missing or invalid settings use defaults. Valid integer ranges: minWidth 240–1200, desktop/tabletHeight 80–640, mobileColumns 1–4, gap 0–48, fadeDuration 0–1000. A missing, malformed or unavailable config file does not prevent gallery startup; after a maximum three-second config wait, the app uses defaults.

### Independent thumbnail loading

Previously, thumbnails already loaded independently: there was no wait-for-all-images step. The update makes this visible:

1. The cube overlay covers initial configuration/folder metadata loading.
2. As soon as the folder is rendered, the overlay closes and each thumbnail slot is visible.
3. Each loading slot shows a subtle animated placeholder.
4. Each image fades in on its own `load` event, without waiting for other images.
5. Failed images retain a static fallback icon. Lazy loading remains enabled for images farther down the page.

The slots retain their dimensions throughout loading. Reduced-motion preferences disable shimmer and fade animation. Repeated/cached thumbnails can still appear nearly simultaneously, as expected.

To see the effect manually, open browser DevTools → Network, enable **Disable cache**, select **Slow 3G**, then reload while DevTools remains open. The automated test also holds one image request and verifies that another image is already visible while the held image is still loading, with the cube overlay dismissed and no tile-size change.

### Focused file changes

New files: `public/gallery-config.json`, `src/app/GalleryConfig.js`.

Updated: `src/main.js` (startup config), `src/shared/dom.js` (individual image state), `src/styles/theme.scss` (minimum width), `src/components/gallery.scss` (config variables/placeholders/fade), `index.html` (commented favicon example), and browser tests/documentation. Your four supplied loader/footer files remain unchanged.


## Learning walkthrough: the SCSS changes

The project already imports `.scss` files and has Sass installed. CSS syntax is valid inside SCSS. These changes use Sass nesting and named breakpoints while retaining the runtime CSS custom properties needed by `gallery-config.json`.

Only `src/styles/theme.scss` and `src/components/gallery.scss` change in this refactor. Other files are the same as the preceding runtime-config checkpoint. This walkthrough is relative to that checkpoint, not the initial shell.

### 1. Understand the two variable types

- `$mobile-breakpoint` is a Sass variable, resolved when Vite compiles the stylesheet. It is suitable for a build-time layout rule.
- `--thumbnail-desktop-height` is a CSS custom property that remains in the browser. `GalleryConfig.js` can update it from JSON without rebuilding.
- `var(--thumbnail-desktop-height, 220px)` means use that custom property, falling back to 220px when it is absent.

Do not replace runtime settings or theme colours with Sass variables: that would remove their current ability to change dynamically. Continue editing `.scss` source, never generated CSS under `dist/`.

### 2. Minimum width: src/styles/theme.scss

Find the existing `body` rule. It is expanded for readability; the behaviour is unchanged:

```scss
body {
	margin: 0;
	min-width: var(--gallery-min-width, 320px);
	background: var(--ui-bg);
	color: var(--ui-text);
	font-family: var(--ui-font);
}
```

The min-width applies to the page layout. Viewports narrower than this value scroll horizontally. Changing `layout.minWidth` in the JSON changes `--gallery-min-width`.

### 3. Breakpoints: top of src/components/gallery.scss

Declare these before the rules that use them:

```scss
$tablet-breakpoint: 1000px;
$mobile-breakpoint: 600px;
```

Existing lower-page media queries also use these names in place of 1000px and 600px. This does not change the breakpoint values.

### 4. Thumbnail rows: src/components/gallery.scss

Replace the existing `.media-grid` rule with the following block. Its pseudo-element and responsive overrides now live inside it:

```scss
.media-grid {
	--row-height: var(--thumbnail-desktop-height, 220px);
	display: flex;
	flex-wrap: wrap;
	gap: var(--thumbnail-gap, 8px);
	padding: 0;
	margin: 0;
	list-style: none;

	// Prevent a sparse last row becoming a single enormous thumbnail.
	&::after {
		content: '';
		flex: 999 1 0;
	}

	@media (max-width: $tablet-breakpoint) {
		--row-height: var(--thumbnail-tablet-height, 190px);
	}

	@media (max-width: $mobile-breakpoint) {
		display: grid;
		grid-template-columns: repeat(var(--thumbnail-mobile-columns, 2), minmax(0, 1fr));

		&::after {
			display: none;
		}
	}
}
```

`&` means the surrounding selector. `&::after` compiles to `.media-grid::after`. Sass moves each nested media query into the appropriate CSS `@media` rule while retaining `.media-grid` as its selector.

`--row-height` starts from the desktop setting and switches to the tablet setting at 1000px. It is inherited by the media tiles. At 600px the grid uses the configured number of equal-width columns. `minmax(0, 1fr)` allows each column to share the width without content forcing it wider.

The `::after` filler prevents the last desktop row from stretching a small number of pictures excessively; it is hidden in the mobile grid.

Remove the old standalone `.media-grid::after` rule and the old `.media-grid`/`.media-grid::after` entries in the bottom responsive blocks, as they are now included above. Keep the unrelated folder/header rules.

### 5. Individual tile: src/components/gallery.scss

The tile's related selectors and mobile sizing now live in its existing block:

```scss
.media-tile {
	position: relative;
	display: grid;
	place-items: center;
	width: 100%;
	height: var(--row-height);
	border: 0;
	border-radius: 5px;
	padding: 0;
	background: var(--ui-surface);
	isolation: isolate;

	> img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: inherit;
	}

	&:hover {
		outline: 2px solid var(--ui-accent);
		outline-offset: 1px;
		z-index: 1;
	}

	> .icon {
		color: var(--ui-muted);
	}

	&:hover .media-caption,
	&:focus-visible .media-caption {
		opacity: 1;
	}

	@media (max-width: $mobile-breakpoint) {
		height: auto;
		aspect-ratio: 1;
	}
}
```

`> img` targets a direct child image; Sass compiles it to `.media-tile > img`. `&:hover` compiles to `.media-tile:hover`. These grouped rules replace their old standalone equivalents; do not keep both versions.

`height: var(--row-height)` uses the inherited desktop/tablet setting. On mobile, `height: auto` and `aspect-ratio: 1` make the tile square using its grid column width. Remove the old `.media-tile` mobile override from the bottom mobile query after moving it here.

### 6. Individual image reveal: src/components/gallery.scss

Replace the existing `.thumbnail` and `.thumbnail.is-loaded` rules with:

```scss
.thumbnail {
	opacity: 0;
	transition: opacity var(--thumbnail-fade-duration, 180ms) ease;

	&.is-loaded {
		opacity: 1;
	}

	@media (prefers-reduced-motion: reduce) {
		transition: none;
	}
}
```

The image starts transparent while the slot stays visible. The existing JavaScript image helper adds `is-loaded` to that same image when its request completes. `&.is-loaded` therefore matches an element with BOTH classes. Writing `.is-loaded` without `&` inside the block would instead match a descendant, which would be wrong here.

Reduced-motion settings turn off the transition while retaining the reveal.

### 7. Loading placeholder: src/components/gallery.scss

Replace the previous combined placeholder rule with:

```scss
.media-tile,
.folder-cover {
	&:has(.is-loading)::before {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: inherit;
		pointer-events: none;
		background: linear-gradient(110deg, transparent 20%, var(--ui-hover) 50%, transparent 80%);
		background-size: 220% 100%;
		animation: thumbnail-shimmer 1.4s linear infinite;

		@media (prefers-reduced-motion: reduce) {
			animation: none;
		}
	}
}
```

```scss
@keyframes thumbnail-shimmer {
	from { background-position: 200% 0; }
	to { background-position: -200% 0; }
}
```

The outer selector list shares this style between media tiles and folder covers. `:has(.is-loading)` is a CSS condition that matches only while the element contains a loading image. `::before` supplies a temporary visual layer without another HTML element. `inset: 0` fills the slot, and `pointer-events: none` keeps the layer from intercepting clicks.

The keyframes move the background gradient. Once the image helper removes `is-loading`, the placeholder selector stops matching. Failed images also leave the loading state and retain the existing fallback icon.

The reduced-motion rules have moved beside the animations they control. Remove the old final reduced-motion block for `.thumbnail` and tile/cover `::before`; the nested rules replace it.

### 8. Verify

Run `npm run build` and `npm test`. Use `/?test=1` for manual checks, then throttle image downloads in browser DevTools to observe each reveal. The refactor should preserve sizing, theme switching, and independent loading.

Sass references:
- https://sass-lang.com/documentation/variables/
- https://sass-lang.com/documentation/style-rules/parent-selector/
