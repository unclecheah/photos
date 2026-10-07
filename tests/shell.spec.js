import { test, expect } from '@playwright/test';

async function ready(page, url = '/') {
	await page.goto(url);
	await expect(page.locator('main')).toHaveAttribute('aria-busy', 'false');
}

test('root media, folder navigation, breadcrumbs and browser Back', async ({ page }) => {
	const errors = [];
	page.on('pageerror', error => errors.push(error.message));
	await ready(page);
	await expect(page.locator('.folder-card')).toHaveCount(3);
	await expect(page.locator('.media-tile')).toHaveCount(9);
	await page.locator('.folder-card').filter({ hasText: 'Japan' }).click();
	await expect(page.locator('h1')).toHaveText('Japan');
	await expect(page.locator('.media-tile')).toHaveCount(12);
	await page.locator('.folder-card').filter({ hasText: 'Kyoto' }).click();
	await expect(page.locator('h1')).toHaveText('Kyoto');
	await page.goBack();
	await expect(page.locator('h1')).toHaveText('Japan');
	await page.getByRole('navigation').getByRole('link', { name: 'Home', exact: true }).click();
	await expect(page.locator('h1')).toHaveText('All photos');
	expect(errors).toEqual([]);
});

test('theme survives refresh and uses the root attribute', async ({ page }) => {
	await ready(page);
	await page.getByRole('button', { name: 'Switch to light theme' }).click();
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
	await page.reload();
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
	await page.getByRole('button', { name: 'Switch to dark theme' }).click();
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
});

test('media selection emits the correct folder sequence; badge only on video', async ({ page }) => {
	await ready(page);
	await page.evaluate(() => {
		document.querySelector('#app').addEventListener('gallery:media-select', event => {
			window.lastSelection = event.detail;
		}, { once: true });
	});
	await expect(page.locator('.video-badge')).toHaveCount(1);
	await page.locator('.media-tile').nth(4).click();
	const selected = await page.evaluate(() => window.lastSelection);
	expect(selected.index).toBe(4);
	expect(selected.item.type).toBe('video');
	expect(selected.items).toHaveLength(9);
	expect(selected.folderPath).toBe('');
});

test('loader stops after errors; retry and empty states work', async ({ page }) => {
	await ready(page, '/?test=1');
	await page.getByText('Shell test controls', { exact: true }).click();
	await page.getByRole('button', { name: 'Simulate error' }).click();
	await expect(page.locator('#loadingOverlay')).toBeVisible();
	await expect(page.locator('h1')).toHaveText('Unable to load this folder');
	await expect(page.locator('#loadingOverlay')).toBeHidden();
	await page.getByRole('button', { name: 'Retry loading folder' }).click();
	await expect(page.locator('h1')).toHaveText('All photos');
	await page.getByRole('button', { name: 'Open empty folder' }).click();
	await expect(page.locator('.empty-state')).toBeVisible();
	await expect(page.locator('.media-section')).toBeHidden();
	await expect(page.locator('footer')).toHaveCount(1);
});

for (const width of [320, 390, 768, 1440]) {
	test(`layout fits ${width}px and footer follows content`, async ({ page }) => {
		await page.setViewportSize({ width, height: 900 });
		await ready(page, '/#folder=Japan');
		expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
		const first = await page.locator('.media-tile').nth(0).boundingBox();
		const second = await page.locator('.media-tile').nth(1).boundingBox();
		if (width <= 600) expect(first.y).toBe(second.y);
		const last = await page.locator('.media-tile').last().boundingBox();
		const footer = await page.locator('footer').boundingBox();
		expect(footer.y).toBeGreaterThanOrEqual(last.y + last.height);
		await ready(page, '/#folder=Family');
		const shortFooter = await page.locator('footer').boundingBox();
		expect(Math.abs(shortFooter.y + shortFooter.height - 900)).toBeLessThan(2);
	});
}

test('deep links and long names stay within a narrow mobile viewport', async ({ page }) => {
	await page.setViewportSize({ width: 320, height: 700 });
	const path = 'Japan/Kyoto/An evening walk through the old streets';
	await ready(page, `/#folder=${encodeURIComponent(path)}`);
	await expect(page.locator('h1')).toHaveText('An evening walk through the old streets');
	expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
	await expect(page.locator('.breadcrumbs [aria-current="page"]')).toHaveText('An evening walk through the old streets');
});

test('rapid route changes show the latest folder and release the loader', async ({ page }) => {
	await ready(page);
	await page.evaluate(async () => {
		location.hash = '#folder=Japan';
		await new Promise(resolve => setTimeout(resolve, 50));
		location.hash = '#folder=Singapore';
	});
	await expect(page.locator('h1')).toHaveText('Singapore');
	await expect(page.locator('#loadingOverlay')).toBeHidden();
	await expect(page.locator('main')).toHaveAttribute('aria-busy', 'false');
});

test('bad image URL shows placeholder without breaking the gallery', async ({ page }) => {
	await page.route('**/demo/1.jpg', route => route.abort());
	await ready(page);
	await expect(page.locator('.media-tile').first().locator('img')).toHaveClass(/image-failed/);
	await expect(page.locator('.media-tile').first().locator('.icon')).toBeVisible();
	await expect(page.locator('#loadingOverlay')).toBeHidden();
});

test('fast thumbnails appear while a slow thumbnail is still loading', async ({ page }) => {
	let release;
	const gate = new Promise(resolve => { release = resolve; });
	await page.route('**/demo/1.jpg', async route => {
		await gate;
		await route.continue();
	});
	try {
		await page.goto('/', { waitUntil: 'domcontentloaded' });
		await expect(page.locator('main')).toHaveAttribute('aria-busy', 'false');
		const slow = page.locator('.media-tile').nth(0).locator('img');
		const fast = page.locator('.media-tile').nth(1).locator('img');
		await expect(fast).toHaveClass(/is-loaded/);
		await expect(fast).toHaveCSS('opacity', '1');
		await expect(slow).toHaveClass(/is-loading/);
		await expect(slow).toHaveCSS('opacity', '0');
		await expect(page.locator('#loadingOverlay')).toBeHidden();
		const before = await slow.boundingBox();
		release();
		await expect(slow).toHaveClass(/is-loaded/);
		await expect(slow).toHaveCSS('opacity', '1');
		expect(await slow.boundingBox()).toEqual(before);
	} finally {
		release();
	}
});

test('runtime config changes height, gap, mobile columns and minimum width', async ({ page }) => {
	await page.route('**/gallery-config.json', route => route.fulfill({
		json: {
			layout: { minWidth: 360 },
			thumbnails: { desktopHeight: 260, tabletHeight: 210, mobileColumns: 1, gap: 16, fadeDuration: 0 }
		}
	}));
	await page.setViewportSize({ width: 1440, height: 900 });
	await ready(page);
	await expect(page.locator('.media-tile').first()).toHaveCSS('height', '260px');
	await expect(page.locator('.media-grid')).toHaveCSS('gap', '16px');
	await page.setViewportSize({ width: 768, height: 900 });
	await expect(page.locator('.media-tile').first()).toHaveCSS('height', '210px');
	await page.setViewportSize({ width: 320, height: 700 });
	await expect(page.locator('body')).toHaveCSS('min-width', '360px');
	const first = await page.locator('.media-tile').nth(0).boundingBox();
	const second = await page.locator('.media-tile').nth(1).boundingBox();
	expect(first.x).toBe(second.x);
	expect(second.y).toBeGreaterThan(first.y);
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(360);
});

test('invalid settings fall back individually', async ({ page }) => {
	await page.route('**/gallery-config.json', route => route.fulfill({
		json: { layout: { minWidth: 'wide' }, thumbnails: { desktopHeight: -1, mobileColumns: 0, gap: 12 } }
	}));
	await page.setViewportSize({ width: 1440, height: 900 });
	await ready(page);
	await expect(page.locator('body')).toHaveCSS('min-width', '320px');
	await expect(page.locator('.media-tile').first()).toHaveCSS('height', '220px');
	await expect(page.locator('.media-grid')).toHaveCSS('gap', '12px');
});

test('missing config does not prevent gallery startup', async ({ page }) => {
	await page.route('**/gallery-config.json', route => route.fulfill({ status: 404, body: '' }));
	await ready(page);
	await expect(page.locator('h1')).toHaveText('All photos');
	await expect(page.locator('body')).toHaveCSS('min-width', '320px');
	await expect(page.locator('#loadingOverlay')).toBeHidden();
});
