import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShInput from './sh-input.svelte';

describe('ShInput', () => {
	it('renders an input element', async () => {
		const screen = render(ShInput);
		await expect.element(screen.getByRole('textbox')).toBeInTheDocument();
	});

	it('forwards class prop via cn', async () => {
		const screen = render(ShInput, { class: 'custom-class' });
		await expect.element(screen.getByRole('textbox')).toHaveClass('custom-class');
	});

	it('forwards placeholder prop', async () => {
		const screen = render(ShInput, { placeholder: 'Digite aqui' });
		await expect.element(screen.getByPlaceholder('Digite aqui')).toBeInTheDocument();
	});

	it('forwards type prop', async () => {
		const screen = render(ShInput, { type: 'email' });
		const input = screen.getByRole('textbox');
		await expect.element(input).toHaveAttribute('type', 'email');
	});

	it('forwards disabled prop', async () => {
		const screen = render(ShInput, { disabled: true });
		await expect.element(screen.getByRole('textbox')).toBeDisabled();
	});
});
