import PhotoSwipe from 'photoswipe';

import 'photoswipe/style.css';
import gCubeOverlay from '../shared/cubeOverlay.js';
import VideoSlide from './VideoSlide.js';
import ViewerThumbnails from './ViewerThumbnails.js';
import './media-viewer.scss';


export default class MediaViewer {
	constructor() {
		this.pswp = null;
		this.thumbnailStrip = null;

		this.viewerLoading = false;
		this.viewerClosing = false;
	}

	createSlide(item) {
		const validType = ['photo', 'video'].includes(item.type);
		const validSize = Number.isFinite(item.width) && Number.isFinite(item.height) && item.width > 0 && item.height > 0;

		if (!validType || !item.src || !validSize) throw new Error(`Invalid media data: ${item.name}`);

		return {
			type: item.type === 'video' ? 'video' : 'image',
			src: item.src,
			msrc: item.thumbnail,
			width: item.width,
			height: item.height,
			alt: item.name
		};
	}

	fitZoom(zoom) {
		const horizontal = zoom.panAreaSize.x / zoom.elementSize.x;
		const vertical = zoom.panAreaSize.y / zoom.elementSize.y;

		return Math.min(horizontal, vertical);
	}

	createOptions(dataSource, index) {
		const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

		return {
			dataSource,
			index,
			mainClass: 'media-viewer',
			bgOpacity: 0.94,
			loop: false,
			preload: [1, 1],

			paddingFn: () => ({
				top: 64,
				bottom: this.thumbnailStrip?.bottomPadding ?? 20,
				left: 16,
				right: 16
			}),
			
			initialZoomLevel: zoom => this.fitZoom(zoom),
			secondaryZoomLevel: zoom => Math.max(1, this.fitZoom(zoom) * 2),
			maxZoomLevel: zoom => Math.max(1, this.fitZoom(zoom) * 4),

			showHideAnimationType: reduceMotion ? 'none' : 'fade'
		};
	}

	async setViewerLoading(loading) {
		if (this.viewerLoading === loading) return;
		this.viewerLoading = loading;

		if (loading) await gCubeOverlay.start({ blocking: false });
		else await gCubeOverlay.stop();
	}

	queueLoadingCheck(pswp) {
		queueMicrotask(async () => {
			if (this.pswp !== pswp || this.viewerClosing) return;

			const content = pswp.currSlide?.content;
			const loading = content?.isLoading() ?? false;
			await this.setViewerLoading(loading);
		});
	}

	bindThumbnailStrip(pswp, items) {
		const strip = new ViewerThumbnails(items, {
			onSelect: index => {
				if (this.pswp === pswp && !this.viewerClosing) pswp.goTo(index);
			},
			onResize: () => {
				if (this.pswp === pswp && pswp.currSlide && !this.viewerClosing) pswp.updateSize(true);
			}
		});

		this.thumbnailStrip = strip;

		pswp.on('uiRegister', () => this.registerThumbnailUi(pswp, strip));
		pswp.on('firstUpdate', () => strip.measure());
		pswp.on('change', () => strip.setCurrent(pswp.currIndex));

		pswp.on('openingAnimationEnd', () => {
			strip.measure();
			pswp.updateSize(true);
		});

		pswp.on('destroy', () => {
			strip.destroy();

			if (this.thumbnailStrip === strip) this.thumbnailStrip = null;
		});
	}

	registerThumbnailUi(pswp, strip) {
		pswp.ui.registerElement({
			name: 'thumbnail-strip',
			className: 'viewer-thumbnails-host',
			appendTo: 'root',
			onInit: container => strip.mount(container)
		});

		pswp.ui.registerElement({
			name: 'thumbnails',
			order: 9,
			isButton: true,
			ariaLabel: 'Thumbnails',
			html: 'Thumbnails',
			onInit: toggleButton => strip.bindToggle(toggleButton),
			onClick: () => strip.toggle()
		});
	}

	bindVideoEvents(pswp) {
		const videos = new Map();

		// Let native video controls handle pointer movement without cancellation.
		pswp.addFilter('preventPointerEvent', (prevent, originalEvent) => {
			const target = originalEvent.target;
			if (target instanceof Element && target.closest('.media-video')) return false;
			return prevent;
		});

		pswp.on('contentLoad', event => {
			const { content } = event;
			if (content.type !== 'video') return;

			event.preventDefault();
			const video = new VideoSlide(content.data, () => this.queueLoadingCheck(pswp));

			videos.set(content, video);
			content.element = video.element;
			content.state = 'loaded';
		});

		pswp.addFilter('isContentLoading', (loading, content) => {
			return videos.get(content)?.isLoading() ?? loading;
		});

		pswp.on('contentActivate', ({ content }) => {
			void videos.get(content)?.activate();
		});

		this.bindVideoCleanup(pswp, videos);
	}

	bindVideoCleanup(pswp, videos) {
		for (const name of ['contentDeactivate', 'contentRemove']) {
			pswp.on(name, ({ content }) => { videos.get(content)?.deactivate(pswp.element); });
		}

		pswp.on('contentDestroy', ({ content }) => {
			videos.get(content)?.destroy();
			videos.delete(content);
		});

		pswp.on('close', () => {
			for (const video of videos.values()) {
				video.deactivate(pswp.element);
			}
		});

		pswp.on('destroy', () => {
			for (const video of videos.values()) video.destroy();
			videos.clear();
		});
	}

	bindViewerEvents(pswp) {
		this.bindVideoEvents(pswp);

		const loadingEvents = [
			'afterInit',
			'change',
			'contentLoadImage',
			'loadComplete',
			'loadError'
		];

		for (const eventName of loadingEvents) {
			pswp.on(eventName, () => { this.queueLoadingCheck(pswp); });
		}

		this.bindViewerCleanup(pswp);
	}

	bindViewerCleanup(pswp) {
		pswp.on('close', async () => {
			if (this.pswp !== pswp) return;
			this.viewerClosing = true;
			await this.setViewerLoading(false);
		});

		pswp.on('destroy', async () => {
			if (this.pswp !== pswp) return;
			this.viewerClosing = true;
			this.pswp = null;
			await this.setViewerLoading(false);
		});
	}

	open(items, index) {
		if (this.pswp) return;
		if (!Number.isInteger(index) || index < 0 || index >= items.length) return;

		const slides = items.map(item => this.createSlide(item));
		const options = this.createOptions(slides, index);

		this.viewerClosing = false;
		this.pswp = new PhotoSwipe(options);
		this.bindViewerEvents(this.pswp);
		this.bindThumbnailStrip(this.pswp, items);
		this.pswp.init();
	}

	close() {
		this.pswp?.close();
	}

	destroy() {
		this.pswp?.destroy();
		this.pswp = null;
	}
}
