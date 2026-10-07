import { element, button, folderUrl } from '../shared/dom.js';

export default class DemoControls {
	constructor(app, source) {
		this.app = app;
		this.source = source;
		this.element = element('details', 'demo-tools');
		this.element.append(element('summary', '', 'Shell test controls'));
		this.element.append(element('p', '', 'Sample images only. Media selection is wired; PhotoSwipe and video playback come next.'));
		const actions = element('div');
		this.addAction(actions, 'Open empty folder', () => { location.hash = folderUrl('Family'); });
		this.addAction(actions, 'Reload with cube loader', async () => { await app.loadFolder(); });
		this.addAction(actions, 'Simulate error', async () => {
			source.failNext = true;
			await app.loadFolder();
		});
		this.element.append(actions);
		app.shell.main.append(this.element);
	}

	addAction(parent, label, callback) {
		const control = button('text-button', label);
		control.textContent = label;
		control.addEventListener('click', callback);
		parent.append(control);
	}
}
