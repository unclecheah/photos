import AppController from './app/AppController.js';
import DemoSource from './demo/DemoSource.js';
import DemoControls from './demo/DemoControls.js';
import GalleryConfig from './app/GalleryConfig.js';
import gCubeOverlay from './shared/cubeOverlay.js';
import './styles/theme.scss';

const config = new GalleryConfig();
config.apply();
const target = document.querySelector('#app');
const source = new DemoSource();
const app = new AppController(target, source);

// Shell-only feedback. Replace this listener with MediaViewer.open(...) later.
const onSelect = event => {
	app.shell.status.textContent = `Selected: ${event.detail.item.name}. The media viewer will be added in the next step.`;
};
target.addEventListener('gallery:media-select', onSelect);

if (new URLSearchParams(location.search).has('test')) new DemoControls(app, source);
app.shell.setBusy(true);
await gCubeOverlay.start();
try {
	await config.load();
	await app.start();
} finally {
	await gCubeOverlay.stop();
}

if (import.meta.hot) {
	import.meta.hot.dispose(() => {
		target.removeEventListener('gallery:media-select', onSelect);
		app.destroy();
	});
}
