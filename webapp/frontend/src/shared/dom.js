export function element(tag, className = '', text = '') {
	const node = document.createElement(tag);
	node.className = className;
	node.textContent = text;
	return node;
}

export function button(className, label) {
	const node = element('button', className);
	node.type = 'button';
	node.setAttribute('aria-label', label);
	return node;
}

export function thumbnail(src) {
	const image = element('img', 'thumbnail is-loading');
	image.alt = '';
	image.loading = 'lazy';
	image.decoding = 'async';
	image.addEventListener('load', () => settleThumbnail(image, true), { once: true });
	image.addEventListener('error', () => settleThumbnail(image, false), { once: true });
	if (src) image.src = src;
	else settleThumbnail(image, false);
	return image;
}

function settleThumbnail(image, loaded) {
	image.classList.remove('is-loading');
	image.classList.add(loaded ? 'is-loaded' : 'image-failed');
}

export function folderUrl(path) {
	return `#folder=${encodeURIComponent(path)}`;
}

export function currentFolder() {
	return new URLSearchParams(location.hash.slice(1)).get('folder') || '';
}
