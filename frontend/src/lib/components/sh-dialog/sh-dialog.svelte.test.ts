import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShDialog from './sh-dialog.svelte';
import ShDialogHeader from './sh-dialog-header.svelte';
import ShDialogFooter from './sh-dialog-footer.svelte';
import ShDialogTitle from './sh-dialog-title.svelte';
import ShDialogDescription from './sh-dialog-description.svelte';

describe('ShDialog', () => {
	it('renders without throwing when closed', () => {
		expect(() => render(ShDialog, { open: false })).not.toThrow();
	});

	it('accepts open prop', () => {
		expect(() => render(ShDialog, { open: true })).not.toThrow();
	});
});

describe('ShDialogHeader', () => {
	it('forwards class prop via cn', async () => {
		const { container } = render(ShDialogHeader, { class: 'header-class' });
		expect(container.querySelector('.header-class')).not.toBeNull();
	});
});

describe('ShDialogFooter', () => {
	it('forwards class prop via cn', async () => {
		const { container } = render(ShDialogFooter, { class: 'footer-class' });
		expect(container.querySelector('.footer-class')).not.toBeNull();
	});
});

describe('ShDialogTitle', () => {
	it('renders without throwing', () => {
		expect(() => render(ShDialogTitle)).not.toThrow();
	});
});

describe('ShDialogDescription', () => {
	it('renders without throwing', () => {
		expect(() => render(ShDialogDescription)).not.toThrow();
	});
});
