import AppController from './app/AppController.js';
import DemoSource from './demo/DemoSource.js';
import DemoControls from './demo/DemoControls.js';
import GalleryConfig from './app/GalleryConfig.js';
import gCubeOverlay from './shared/cubeOverlay.js';
import MediaViewer from './components/MediaViewer.js';
import HttpSource from './data/HttpSource.js';
import './styles/theme.scss';

const config = new GalleryConfig();
config.apply();
const target = document.querySelector('#app');
const params = new URLSearchParams(location.search);

const source = params.get('source') === 'http'
	? new HttpSource({ endpoint: '/api/folder.php' })
	: new DemoSource();

const app = new AppController(target, source);
const mediaViewer = new MediaViewer();

const onSelect = event => {
	const { items, index } = event.detail;
	app.shell.status.textContent = '';

	try {
		mediaViewer.open(items, index);
	} catch (error) {
		mediaViewer.destroy();
		app.shell.status.textContent = 'Unable to open this media item.';
		console.error('Media viewer failed:', error);
	}
};
target.addEventListener('gallery:media-select', onSelect);

if (params.has('test') && source instanceof DemoSource) new DemoControls(app, source);

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
		mediaViewer.destroy();
		app.destroy();
	});
}
