import { element, button, thumbnail } from '../shared/dom.js';
import { icon } from '../shared/icons.js';
import './viewer-thumbnails.scss';

let stripSequence = 0;

export default class ViewerThumbnails {
	constructor(items, { onSelect, onResize }) {
		this.onSelect = onSelect;
		this.onResize = onResize;
		this.visible = true;
		this.currentIndex = -1;
		this.bottomPadding = 112;
		this.frame = null;
		this.events = new AbortController();

		this.build(items);
	}

	build(items) {
		this.element = element('nav', 'viewer-thumbnails');
		this.element.id = `viewer-thumbnails-${++stripSequence}`;
		this.element.setAttribute('aria-label', 'Choose a photo or video');

		this.track = element('ul', 'viewer-thumbnails__track');

		this.buttons = items.map((item, index) => {
			const tile = this.createButton(item, index);
			const row = element('li', 'viewer-thumbnails__item');

			row.append(tile);
			this.track.append(row);
			return tile;
		});

		this.element.append(this.track);
		this.element.addEventListener('wheel', event => { event.stopPropagation(); }, { passive: true, signal: this.events.signal });
	}

	createButton(item, index) {
		const type = item.type === 'video' ? 'Video' : 'Photo';
		const tile = button('viewer-thumbnail', `${index + 1}. ${type}: ${item.name}`);

		tile.title = item.name;
		tile.tabIndex = -1;
		tile.append(icon('image'), thumbnail(item.thumbnail));

		if (item.type === 'video') {
			const badge = element('span', 'viewer-thumbnail__badge');
			badge.setAttribute('aria-hidden', 'true');
			badge.append(icon('film'));
			tile.append(badge);
		}

		tile.addEventListener('click', () => { this.onSelect(index); }, { signal: this.events.signal });

		return tile;
	}

	mount(container) {
		container.append(this.element);

		this.observer = new ResizeObserver(() => this.measure());
		this.observer.observe(this.element);
	}

	bindToggle(toggleButton) {
		this.toggleButton = toggleButton;
		toggleButton.setAttribute('aria-controls', this.element.id);
		toggleButton.setAttribute('aria-expanded', String(this.visible));
		toggleButton.title = 'Show or hide thumbnails';
	}

	toggle() {
		this.visible = !this.visible;

		if (!this.visible && this.element.contains(document.activeElement)) {
			this.toggleButton?.focus({ preventScroll: true });
		}

		this.element.hidden = !this.visible;
		this.toggleButton?.setAttribute('aria-expanded', String(this.visible));
		this.measure();
	}

	measure() {
		if (!this.element.isConnected) return;

		const padding = this.visible ? Math.ceil(this.element.getBoundingClientRect().height) + 16 : 20;

		if (padding !== this.bottomPadding) {
			this.bottomPadding = padding;
			this.onResize();
		}

		this.queueReveal();
	}

	setCurrent(index) {
		const current = this.buttons[index];
		if (!current) return;

		const moveFocus = this.element.contains(document.activeElement);
		const previous = this.buttons[this.currentIndex];

		if (previous) {
			previous.removeAttribute('aria-current');
			previous.tabIndex = -1;
		}

		this.currentIndex = index;
		current.setAttribute('aria-current', 'true');
		current.tabIndex = 0;

		if (moveFocus) current.focus({ preventScroll: true });
		this.queueReveal();
	}

	queueReveal() {
		cancelAnimationFrame(this.frame);

		this.frame = requestAnimationFrame(() => {
			this.frame = null;
			this.revealCurrent();
		});
	}

	revealCurrent() {
		const current = this.buttons[this.currentIndex];
		if (!this.visible || !current || !this.element.isConnected) return;

		const track = this.track.getBoundingClientRect();
		const tile = current.getBoundingClientRect();
		const left = track.left + 4;
		const right = track.right - 4;

		if (tile.left < left) this.track.scrollLeft += tile.left - left;
		else if (tile.right > right) this.track.scrollLeft += tile.right - right;
	}

	destroy() {
		cancelAnimationFrame(this.frame);
		this.observer?.disconnect();
		this.events.abort();
		this.element.remove();
	}
}
