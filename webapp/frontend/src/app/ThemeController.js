import { icon } from '../shared/icons.js';

const THEMES = ['light', 'dark', 'blue', 'sepia'];
const THEME_COLOURS = {
	light: '#edf3fa',
	dark: '#101720',
	blue: '#0c2038',
	sepia: '#f3eadb'
};

export default class ThemeController {
	constructor(button) {
		this.button = button;
		this.handleClick = () => this.cycleTheme();
		this.button.addEventListener('click', this.handleClick);
		this.apply(this.readSavedTheme());
	}

	readSavedTheme() {
		try {
			const saved = localStorage.getItem('photo-site-theme');
			return THEMES.includes(saved) ? saved : 'dark';
		} catch {
			return 'dark';
		}
	}

	nextTheme() {
		const index = THEMES.indexOf(this.theme);
		return THEMES[(index + 1) % THEMES.length];
	}

	cycleTheme() {
		this.apply(this.nextTheme());
	}

	apply(theme) {
		this.theme = THEMES.includes(theme) ? theme : 'dark';
		document.documentElement.dataset.theme = this.theme;
		this.updateButton();
		document.querySelector('meta[name="theme-color"]')?.setAttribute(
			'content', THEME_COLOURS[this.theme]
		);
		try { localStorage.setItem('photo-site-theme', this.theme); }
		catch { /* Theme switching still works when storage is unavailable. */ }
	}

	updateButton() {
		const next = this.nextTheme();
		const label = `Current theme: ${this.theme}. Switch to ${next} theme`;
		this.button.setAttribute('aria-label', label);
		this.button.title = label;
		// Reuse the existing icons: sun for a light palette, moon for a dark one.
		const nextIsLight = ['light', 'sepia'].includes(next);
		this.button.replaceChildren(icon(nextIsLight ? 'sun' : 'moon'));
	}

	destroy() {
		this.button.removeEventListener('click', this.handleClick);
	}
}
