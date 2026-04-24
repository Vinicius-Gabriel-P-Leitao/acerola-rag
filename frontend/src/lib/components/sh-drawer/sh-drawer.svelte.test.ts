import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShDrawer from './sh-drawer.svelte';
import ShDrawerHeader from './sh-drawer-header.svelte';
import ShDrawerFooter from './sh-drawer-footer.svelte';
import ShDrawerTitleWrapper from './sh-drawer-title-wrapper.test.svelte';
import ShDrawerDescriptionWrapper from './sh-drawer-description-wrapper.test.svelte';

describe('ShDrawer', () => {
	it('renders without throwing when closed', () => {
		expect(() => render(ShDrawer, { open: false })).not.toThrow();
	});

	it('accepts open prop', () => {
		expect(() => render(ShDrawer, { open: true })).not.toThrow();
	});
});

describe('ShDrawerHeader', () => {
	it('forwards class prop via cn', async () => {
		const { container } = render(ShDrawerHeader, { class: 'header-class' });
		expect(container.querySelector('.header-class')).not.toBeNull();
	});
});

describe('ShDrawerFooter', () => {
	it('forwards class prop via cn', async () => {
		const { container } = render(ShDrawerFooter, { class: 'footer-class' });
		expect(container.querySelector('.footer-class')).not.toBeNull();
	});
});

describe('ShDrawerTitle', () => {
	it('renders without throwing', () => {
		expect(() => render(ShDrawerTitleWrapper)).not.toThrow();
	});
});

describe('ShDrawerDescription', () => {
	it('renders without throwing', () => {
		expect(() => render(ShDrawerDescriptionWrapper)).not.toThrow();
	});
});
