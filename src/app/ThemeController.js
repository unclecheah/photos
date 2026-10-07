import { icon } from '../shared/icons.js';

export default class ThemeController {
	constructor(button) {
		this.button = button;
		this.handleClick = () => this.apply(this.theme === 'dark' ? 'light' : 'dark');
		this.button.addEventListener('click', this.handleClick);
		this.apply(this.readSavedTheme());
	}

	readSavedTheme() {
		try { return localStorage.getItem('photo-site-theme') === 'light' ? 'light' : 'dark'; }
		catch { return 'dark'; }
	}

	apply(theme) {
		this.theme = theme === 'light' ? 'light' : 'dark';
		document.documentElement.dataset.theme = this.theme;
		const label = `Switch to ${this.theme === 'dark' ? 'light' : 'dark'} theme`;
		this.button.setAttribute('aria-label', label);
		this.button.title = label;
		this.button.replaceChildren(icon(this.theme === 'dark' ? 'sun' : 'moon'));
		document.querySelector('meta[name="theme-color"]')?.setAttribute('content',
			this.theme === 'dark' ? '#101720' : '#edf3fa');
		try { localStorage.setItem('photo-site-theme', this.theme); }
		catch { /* Theme switching still works when storage is unavailable. */ }
	}

	destroy() {
		this.button.removeEventListener('click', this.handleClick);
	}
}
