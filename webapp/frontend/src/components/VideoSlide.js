import { element } from '../shared/dom.js';

export default class VideoSlide {
	constructor(data, onChange) {
		this.data = data;
		this.onChange = onChange;
		this.active = false;
		this.failed = false;
		this.requestId = 0;
		this.events = new AbortController();

		this.build();
		this.bindEvents();
		this.protectControls();
	}

	build() {
		this.element = element('div', 'media-video');
		this.video = element('video', 'media-video__player');
		this.video.controls = true;
		this.video.playsInline = true;
		this.video.preload = 'none';
		this.video.setAttribute('aria-label', this.data.alt);

		if (this.data.msrc) this.video.poster = this.data.msrc;

		this.message = element('p', 'media-video__message');
		this.message.setAttribute('role', 'status');
		this.message.hidden = true;

		this.element.append(this.video, this.message);
	}

	bindEvents() {
		const eventNames = ['loadstart', 'loadeddata', 'canplay', 'play', 'playing', 'waiting',
			'seeking', 'seeked', 'pause', 'ended', 'error'
		];

		for (const name of eventNames) {
			this.video.addEventListener(
				name,
				() => this.handleMediaEvent(name),
				{ signal: this.events.signal }
			);
		}
	}

	handleMediaEvent(name) {
		if (!this.active) return;

		if (name === 'error') {
			this.failed = true;
			this.setMessage('Unable to load this video.');
		} else if (name === 'playing') {
			this.failed = false;
			this.setMessage('');
		}

		this.onChange();
	}

	protectControls() {
		// Keep the whole control gesture away from PhotoSwipe, including scrubbing.
		// Do not preventDefault: native video controls need their browser behaviour.
		const eventNames = [
			'pointerdown', 'pointermove', 'pointerup', 'pointercancel',
			'mousedown', 'mousemove', 'mouseup',
			'touchstart', 'touchmove', 'touchend', 'touchcancel',
			'click', 'dblclick', 'wheel'
		];

		for (const name of eventNames) {
			this.element.addEventListener(
				name,
				event => event.stopPropagation(),
				{ signal: this.events.signal }
			);
		}

		this.element.addEventListener('keydown', event => {
			if (!['Escape', 'Tab'].includes(event.key)) event.stopPropagation();
		}, { signal: this.events.signal });
	}

	setMessage(text) {
		this.message.textContent = text;
		this.message.hidden = !text;
	}

	isLoading() {
		if (!this.active || this.failed || this.video.error) return false;

		const needsFirstFrame = this.video.readyState < 2;
		const buffering = !this.video.paused && this.video.readyState < 3;

		return needsFirstFrame || buffering;
	}

	async activate() {
		if (this.active) return;

		this.active = true;
		this.failed = false;
		const requestId = ++this.requestId;

		this.setMessage('');
		this.video.preload = 'auto';
		this.video.src = this.data.src;
		this.video.load();
		this.onChange();

		try {
			await this.video.play();
		} catch (error) {
			if (!this.active || requestId !== this.requestId) return;
			this.handlePlayError(error);
		}

		this.onChange();
	}

	handlePlayError(error) {
		if (error.name === 'NotAllowedError') {
			this.setMessage('Press Play to start this video.');
		} else if (error.name !== 'AbortError') {
			this.failed = true;
			this.setMessage('Unable to play this video.');
		}
	}

	deactivate(focusTarget) {
		if (!this.active) return;

		this.active = false;
		this.requestId++;

		if (this.element.contains(document.activeElement)) {
			focusTarget?.focus({ preventScroll: true });
		}

		this.video.pause();
		this.video.removeAttribute('src');
		this.video.preload = 'none';
		this.video.load();

		this.setMessage('');
		this.onChange();
	}

	destroy() {
		this.events.abort();
		this.deactivate();
		this.element.remove();
	}
}
