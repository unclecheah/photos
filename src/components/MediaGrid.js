import { element, button, thumbnail } from '../shared/dom.js';
import { icon } from '../shared/icons.js';

export default class MediaGrid {
	constructor(onSelect) {
		this.onSelect = onSelect;
		this.element = element('ul', 'media-grid');
	}

	render(items) {
		this.element.replaceChildren(...items.map((item, index) => this.createTile(item, index)));
	}

	createTile(item, index) {
		const row = element('li', 'media-cell');
		const ratio = item.width / item.height;
		row.style.setProperty('--ratio', Number.isFinite(ratio) && ratio > 0 ? ratio : 1.5);
		const tile = button('media-tile', `${item.type === 'video' ? 'Video' : 'Photo'}: ${item.name}`);
		tile.append(icon('image'), thumbnail(item.thumbnail));
		tile.append(element('span', 'media-caption', item.name));
		if (item.type === 'video') this.addVideoBadge(tile, item);
		tile.addEventListener('click', () => this.onSelect(index, item));
		row.append(tile);
		return row;
	}

	addVideoBadge(tile, item) {
		const badge = element('span', 'video-badge');
		badge.title = 'Video';
		badge.append(icon('film'));
		tile.append(badge);
		if (item.duration) tile.append(element('span', 'video-duration', item.duration));
	}
}
