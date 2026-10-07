import GalleryShell from '../components/GalleryShell.js';
import gCubeOverlay from '../shared/cubeOverlay.js';
import gFooter from '../shared/footer.js';
import { currentFolder } from '../shared/dom.js';

export default class AppController {
	constructor(target, source) {
		this.target = target;
		this.source = source;
		this.requestId = 0;
		this.disposed = false;
		this.shell = new GalleryShell(target, {
			onMediaSelect: (index, item) => this.selectMedia(index, item),
			onRetry: () => this.loadFolder()
		});
		gFooter.mount(this.shell.element);
		this.handleHashChange = () => this.loadFolder();
	}

	async start() {
		window.addEventListener('hashchange', this.handleHashChange);
		await this.loadFolder(false);
	}

	async loadFolder(focusHeading = true) {
		const requestId = ++this.requestId;
		const isCurrent = () => !this.disposed && requestId === this.requestId;
		this.shell.setBusy(true);
		try {
			await gCubeOverlay.start();
			const folder = await this.source.getFolder(currentFolder());
			if (!isCurrent()) return;
			this.folder = folder;
			this.shell.setBusy(false);
			this.shell.render(folder, focusHeading);
			if (focusHeading) window.scrollTo(0, 0);
		} catch (error) {
			if (!isCurrent()) return;
			console.warn('Folder loading failed:', error.message);
			this.folder = null;
			this.shell.setBusy(false);
			this.shell.showError();
		} finally {
			await gCubeOverlay.stop();
			if (isCurrent()) this.shell.setBusy(false);
		}
	}

	selectMedia(index, item) {
		if (!this.folder) return;
		// Future MediaViewer integration attaches here. No fake playback or zoom.
		this.target.dispatchEvent(new CustomEvent('gallery:media-select', {
			bubbles: true,
			detail: { index, item, items: this.folder.media, folderPath: this.folder.path }
		}));
	}

	destroy() {
		this.disposed = true;
		this.requestId++;
		window.removeEventListener('hashchange', this.handleHashChange);
		gFooter.unmount();
		this.shell.destroy();
	}
}
