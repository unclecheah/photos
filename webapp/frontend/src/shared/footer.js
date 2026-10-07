import $ from 'jquery';
import './footer.scss';

class Footer {
	constructor({ text = '© unclecheah' } = {}) {
		this.$element = $('<footer>', { class: 'app-footer', });
		this.$text = $('<small>', { class: 'app-footer__text', })
			.text(text)
			.appendTo(this.$element);

		this.isMounted = false;
	}

	mount(target = document.body) {
		// if (this.isMounted) return this;

		this.$element.appendTo(target);
		this.isMounted = true;

		return this;
	}

	setText(text) {
		this.$text.text(text);

		return this;
	}

	unmount() {
		this.$element.detach();
		this.isMounted = false;

		return this;
	}
}

const gFooter = new Footer ();
export default gFooter;
