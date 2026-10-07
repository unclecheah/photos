export default class HttpSource {
	constructor({ endpoint, timeout = 10000 }) {
		this.endpoint = new URL(endpoint, document.baseURI);
		this.timeout = timeout;
	}

	async getFolder(path = '') {
		const url = new URL(this.endpoint);
		url.searchParams.set('path', path);

		const controller = new AbortController();
		const timer = setTimeout(() => controller.abort(), this.timeout);

		try {
			const response = await fetch(url, {
				headers: { Accept: 'application/json' },
				cache: 'no-store',
				signal: controller.signal
			});

			const folder = await this.readResponse(response);
			this.validateFolder(folder, path);
			return folder;

		} catch (error) {
			if (controller.signal.aborted) throw new Error('The folder request timed out.');
			throw error;

		} finally {
			clearTimeout(timer);
		}
	}

	async readResponse(response) {
		if (!response.ok) throw new Error(`Folder request failed: HTTP ${response.status}.`);

		const contentType = response.headers.get('content-type') ?? '';

		if (!contentType.toLowerCase().includes('application/json')) {
			throw new Error('Expected folder JSON, but the server returned another content type.');
		}

		return await response.json();
	}

	validateFolder(folder, requestedPath) {
		const validHeader = folder
			&& folder.path === requestedPath
			&& typeof folder.name === 'string';

		const validLists = Array.isArray(folder?.breadcrumbs)
			&& Array.isArray(folder?.folders)
			&& Array.isArray(folder?.media);

		if (!validHeader || !validLists) throw new Error('The server returned an invalid folder response.');

		const validNavigation = folder.breadcrumbs.every(item => this.isNamedPath(item))
			&& folder.folders.every(item => this.isNamedPath(item));

		if (!validNavigation) {
			throw new Error('The folder response contains invalid navigation data.');
		}

		if (!folder.media.every(item => this.isValidMedia(item))) {
			throw new Error('The folder response contains invalid media data.');
		}
	}

	isNamedPath(item) {
		return item
			&& typeof item.name === 'string'
			&& typeof item.path === 'string';
	}

	isValidMedia(item) {
		return item
			&& typeof item.id === 'string'
			&& typeof item.name === 'string'
			&& ['photo', 'video'].includes(item.type)
			&& typeof item.src === 'string'
			&& item.src.length > 0
			&& (item.thumbnail == null || typeof item.thumbnail === 'string')
			&& Number.isFinite(item.width)
			&& Number.isFinite(item.height)
			&& item.width > 0
			&& item.height > 0;
	}
}
