import { element, button, folderUrl } from '../shared/dom.js';
import Breadcrumbs from './Breadcrumbs.js';
import FolderGrid from './FolderGrid.js';
import MediaGrid from './MediaGrid.js';
import ThemeController from '../app/ThemeController.js';
import './gallery.scss';

export default class GalleryShell {
	constructor(target, { onMediaSelect, onRetry }) {
		this.element = element('div', 'gallery-shell');
		this.breadcrumbs = new Breadcrumbs();
		this.folders = new FolderGrid();
		this.media = new MediaGrid(onMediaSelect);
		this.buildHeader();
		this.buildContent(onRetry);
		target.replaceChildren(this.element);
	}

	buildHeader() {
		const header = element('header', 'site-header');
		const home = element('a', 'brand', 'unclecheah');
		home.href = folderUrl('');
		home.append(element('span', '', ' / photos'));
		const themeButton = button('icon-button', 'Switch theme');
		header.append(home, themeButton);
		this.theme = new ThemeController(themeButton);
		this.element.append(header);
	}

	buildContent(onRetry) {
		this.main = element('main', 'gallery-main');
		this.main.id = 'gallery-content';
		this.heading = element('h1');
		this.heading.tabIndex = -1;
		this.meta = element('p', 'folder-meta');
		this.status = element('p', 'gallery-status');
		this.status.setAttribute('role', 'status');
		this.status.setAttribute('aria-live', 'polite');
		this.empty = element('p', 'empty-state', 'This folder is empty.');
		this.mediaSection = element('section', 'media-section');
		this.mediaSection.setAttribute('aria-label', 'Photos and videos');
		this.mediaSection.append(element('h2', '', 'Photos & videos'), this.media.element);
		this.retry = button('text-button', 'Retry loading folder');
		this.retry.textContent = 'Try again';
		this.retry.addEventListener('click', onRetry);
		this.retry.hidden = true;
		this.main.append(this.breadcrumbs.element, this.heading, this.meta,
			this.folders.element, this.mediaSection, this.empty, this.status, this.retry);
		this.element.append(this.main);
	}

	render(folder, focusHeading = false) {
		this.heading.textContent = folder.name;
		this.meta.textContent = this.describe(folder);
		this.breadcrumbs.render(folder.breadcrumbs);
		this.folders.render(folder.folders);
		this.media.render(folder.media);
		this.folders.element.hidden = folder.folders.length === 0;
		this.mediaSection.hidden = folder.media.length === 0;
		this.empty.hidden = folder.folders.length + folder.media.length > 0;
		this.retry.hidden = true;
		this.status.textContent = '';
		document.title = `${folder.name} | unclecheah photos`;
		if (focusHeading) this.heading.focus({ preventScroll: true });
	}

	describe(folder) {
		const photos = folder.media.filter(item => item.type === 'photo').length;
		const videos = folder.media.length - photos;
		return `${folder.folders.length} folders · ${photos} photos · ${videos} videos`;
	}

	setBusy(busy) {
		this.main.setAttribute('aria-busy', String(busy));
		this.main.inert = busy;
	}

	showError() {
		this.heading.textContent = 'Unable to load this folder';
		this.meta.textContent = '';
		this.breadcrumbs.render([{ name: 'Home', path: '' }, { name: 'Unavailable', path: null }]);
		this.folders.element.hidden = true;
		this.mediaSection.hidden = true;
		this.empty.hidden = true;
		this.status.textContent = 'Please try again, or return to Home.';
		this.retry.hidden = false;
		this.heading.focus({ preventScroll: true });
	}

	destroy() {
		this.theme.destroy();
		this.element.remove();
	}
}
