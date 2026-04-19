import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShAlert from './sh-alert.svelte';
import ShAlertTitle from './sh-alert-title.svelte';
import ShAlertDescription from './sh-alert-description.svelte';

describe('ShAlert', () => {
	it('renders with data-slot attribute', async () => {
		const { container } = render(ShAlert);
		expect(container.querySelector('[data-slot="alert"]')).not.toBeNull();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShAlert, { class: 'custom-alert' });
		expect(container.querySelector('.custom-alert')).not.toBeNull();
	});

	it('forwards variant prop', async () => {
		expect(() => render(ShAlert, { variant: 'destructive' })).not.toThrow();
	});
});

describe('ShAlertTitle', () => {
	it('renders without throwing', () => {
		expect(() => render(ShAlertTitle)).not.toThrow();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShAlertTitle, { class: 'title-class' });
		expect(container.querySelector('.title-class')).not.toBeNull();
	});
});

describe('ShAlertDescription', () => {
	it('renders without throwing', () => {
		expect(() => render(ShAlertDescription)).not.toThrow();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShAlertDescription, { class: 'desc-class' });
		expect(container.querySelector('.desc-class')).not.toBeNull();
	});
});
