// Each entry is: CSS variable, unit, default, minimum, maximum.
const settings = {
	layout: {
		minWidth: ['--gallery-min-width', 'px', 320, 240, 1200]
	},
	thumbnails: {
		desktopHeight: ['--thumbnail-desktop-height', 'px', 220, 80, 640],
		tabletHeight: ['--thumbnail-tablet-height', 'px', 190, 80, 640],
		mobileColumns: ['--thumbnail-mobile-columns', '', 2, 1, 4],
		gap: ['--thumbnail-gap', 'px', 8, 0, 48],
		fadeDuration: ['--thumbnail-fade-duration', 'ms', 180, 0, 1000]
	}
};

export default class GalleryConfig {
	async load() {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort(), 3000);
		try {
			const response = await fetch(`${import.meta.env.BASE_URL}gallery-config.json`, {
				cache: 'no-store', signal: controller.signal
			});
			if (!response.ok) throw new Error(`HTTP ${response.status}`);
			this.apply(await response.json());
		} catch (error) {
			console.warn('Gallery config unavailable; using defaults:', error.message);
			this.apply();
		} finally {
			clearTimeout(timeout);
		}
	}

	apply(config = {}) {
		for (const [group, entries] of Object.entries(settings)) {
			for (const [name, rule] of Object.entries(entries)) {
				this.applySetting(config?.[group]?.[name], rule);
			}
		}
	}

	applySetting(value, [property, unit, fallback, min, max]) {
		const valid = Number.isInteger(value) && value >= min && value <= max;
		document.documentElement.style.setProperty(property, `${valid ? value : fallback}${unit}`);
	}
}
