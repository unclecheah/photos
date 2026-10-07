const asset = (name, extension = 'jpg') => `${import.meta.env.BASE_URL}demo/${name}.${extension}`;
const names = ['Temple at dusk', 'City lights', 'Old streets', 'Quiet afternoon', 'Mountain view', 'Along the river'];
const sampleSizes = [
	[800, 534],
	[800, 519],
	[800, 533],
	[800, 533],
	[800, 534],
	[800, 617]
];

function demoVideo(id) {
	return {
		id,
		name: 'Flowers in the breeze',
		type: 'video',
		thumbnail: asset('5'),
		src: asset('flower', 'mp4'),
		width: 960,
		height: 540,
		duration: '0:05'
	};
}

function media(count, prefix = 'sample') {
	return Array.from({ length: count }, (_, index) => {
		const id = `${prefix}-${index}`;

		if (index % 5 === 4) return demoVideo(id);

		const sampleIndex = index % sampleSizes.length;
		const [width, height] = sampleSizes[sampleIndex];
		const imageUrl = asset(String(sampleIndex + 1));

		return {
			id,
			name: names[index % names.length],
			type: 'photo',
			thumbnail: imageUrl,
			src: imageUrl,
			width,
			height,
			duration: null
		};
	});
}

const records = {
	'': { name: 'All photos', children: ['Japan', 'Singapore', 'Family'], media: media(9) },
	Japan: { name: 'Japan', children: ['Japan/Kyoto', 'Japan/Tokyo', 'Japan/Nara'], media: media(12, 'japan') },
	'Japan/Kyoto': { name: 'Kyoto', children: ['Japan/Kyoto/An evening walk through the old streets'], media: media(6, 'kyoto') },
	'Japan/Kyoto/An evening walk through the old streets': { name: 'An evening walk through the old streets', children: [], media: media(3, 'walk') },
	'Japan/Tokyo': { name: 'Tokyo', children: [], media: media(8, 'tokyo') },
	'Japan/Nara': { name: 'Nara', children: [], media: media(2, 'nara') },
	Singapore: { name: 'Singapore', children: [], media: media(4, 'singapore') },
	Family: { name: 'Family', children: [], media: [] }
};

export default class DemoSource {
	constructor({ delay = 300 } = {}) {
		this.delay = delay;
		this.failNext = false;
	}

	async getFolder(path = '') {
		// Deliberate demo delay so the loading overlay is easy to check.
		await new Promise(resolve => setTimeout(resolve, this.delay));
		if (this.failNext) {
			this.failNext = false;
			throw new Error('Simulated loading failure');
		}
		if (!Object.hasOwn(records, path)) throw new Error('Folder not found');
		const record = records[path];
		return {
			path, name: record.name, breadcrumbs: this.breadcrumbs(path),
			folders: record.children.map((child, index) => this.folder(child, index)),
			media: structuredClone(record.media)
		};
	}

	folder(path, index) {
		const record = records[path];
		return {
			path, name: record.name,
			itemCount: record.children.length + record.media.length,
			cover: record.media.length || record.children.length ? asset(String(index % 6 + 1)) : null
		};
	}

	breadcrumbs(path) {
		const result = [{ name: 'Home', path: '' }];
		const parts = path.split('/').filter(Boolean);
		parts.forEach((name, index) => result.push({ name, path: parts.slice(0, index + 1).join('/') }));
		return result;
	}
}
