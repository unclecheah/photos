import { element, folderUrl } from '../shared/dom.js';

export default class Breadcrumbs {
	constructor() {
		this.element = element('nav', 'breadcrumbs');
		this.element.setAttribute('aria-label', 'Folder breadcrumbs');
	}

	render(items) {
		const list = element('ol');
		items.forEach((item, index) => {
			const row = element('li');
			const current = index === items.length - 1;
			const link = element(current ? 'span' : 'a', '', item.name);
			if (current) link.setAttribute('aria-current', 'page');
			else link.href = folderUrl(item.path);
			row.append(link);
			list.append(row);
		});
		this.element.replaceChildren(list);
	}
}
