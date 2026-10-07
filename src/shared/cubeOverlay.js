import $ from 'jquery';
import './cubeOverlay.scss';


class CubeOverlay {
	#active;        // keeps count of how many times start and stop are called. Each start must have a corresponding stop

	constructor () {
		this.#active = 0;
	}

	start = async (options = {}) => {
		this.#active ++;
		if (this.#active > 1) return;

		if ($('#loadingOverlay').length == 0) {         //  create div for overlay if not already there
			$("<div>", {
				id: "loadingOverlay",
				class: "loading-overlay d-none"
			}).appendTo ("body");
		}

		const overlay = $('#loadingOverlay');
		overlay.append(`
			<div class='spinner'>
				<div></div>
				<div></div>
				<div></div>
				<div></div>
				<div></div>
				<div></div>
			</div>
		`);

		const blocking = options.blocking !== false;
		overlay.removeClass ('d-none');

		if (blocking) overlay.removeClass ('non-blocking');
		else overlay.addClass ('non-blocking');

		await new Promise(resolve => {
			requestAnimationFrame(() => {
				if (this.#active > 0) overlay.addClass('show');

				resolve();
			});
		});
	}


	stop = async () => {
		if (this.#active === 0) return;

		this.#active --;
		if (this.#active > 0) return;

		$('#loadingOverlay')
			.removeClass('show').addClass('d-none non-blocking')
			.empty();
	}
}

const gCubeOverlay = new CubeOverlay ();
export default gCubeOverlay;
