import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShInputGroup from './sh-input-group.svelte';
import ShInputGroupInput from './sh-input-group-input.svelte';
import ShInputGroupTextarea from './sh-input-group-textarea.svelte';
import ShInputGroupText from './sh-input-group-text.svelte';

describe('ShInputGroup', () => {
	it('renders without throwing', () => {
		expect(() => render(ShInputGroup)).not.toThrow();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShInputGroup, { class: 'group-class' });
		expect(container.querySelector('.group-class')).not.toBeNull();
	});
});

describe('ShInputGroupInput', () => {
	it('renders an input element', async () => {
		const screen = render(ShInputGroupInput);
		await expect.element(screen.getByRole('textbox')).toBeInTheDocument();
	});

	it('forwards placeholder prop', async () => {
		const screen = render(ShInputGroupInput, { placeholder: 'Search...' });
		await expect.element(screen.getByPlaceholder('Search...')).toBeInTheDocument();
	});
});

describe('ShInputGroupTextarea', () => {
	it('renders a textarea element', async () => {
		const screen = render(ShInputGroupTextarea);
		await expect.element(screen.getByRole('textbox')).toBeInTheDocument();
	});
});

describe('ShInputGroupText', () => {
	it('renders without throwing', () => {
		expect(() => render(ShInputGroupText)).not.toThrow();
	});
});
