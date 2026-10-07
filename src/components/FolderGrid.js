import { element, thumbnail, folderUrl } from '../shared/dom.js';
import { icon } from '../shared/icons.js';

export default class FolderGrid {
	constructor() {
		this.element = element('ul', 'folder-grid');
		this.element.setAttribute('aria-label', 'Subfolders');
	}

	render(folders) {
		this.element.replaceChildren(...folders.map(folder => this.createCard(folder)));
	}

	createCard(folder) {
		const row = element('li');
		const link = element('a', 'folder-card');
		link.href = folderUrl(folder.path);
		const cover = element('span', 'folder-cover');
		cover.append(icon('image'), thumbnail(folder.cover));
		const copy = element('span', 'folder-copy');
		copy.append(element('strong', '', folder.name));
		if (Number.isInteger(folder.itemCount)) {
			copy.append(element('small', '', `${folder.itemCount} items`));
		}
		const arrow = icon('chevron');
		arrow.classList.add('folder-arrow');
		link.append(cover, icon('folder'), copy, arrow);
		row.append(link);
		return row;
	}
}
