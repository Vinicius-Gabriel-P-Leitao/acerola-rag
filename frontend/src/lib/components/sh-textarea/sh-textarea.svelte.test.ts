import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShTextarea from './sh-textarea.svelte';

describe('ShTextarea', () => {
	it('renders a textarea element', async () => {
		const screen = render(ShTextarea);
		await expect.element(screen.getByRole('textbox')).toBeInTheDocument();
	});

	it('forwards class prop via cn', async () => {
		const screen = render(ShTextarea, { class: 'custom-class' });
		await expect.element(screen.getByRole('textbox')).toHaveClass('custom-class');
	});

	it('forwards placeholder prop', async () => {
		const screen = render(ShTextarea, { placeholder: 'Escreva aqui' });
		await expect.element(screen.getByPlaceholder('Escreva aqui')).toBeInTheDocument();
	});

	it('forwards disabled prop', async () => {
		const screen = render(ShTextarea, { disabled: true });
		await expect.element(screen.getByRole('textbox')).toBeDisabled();
	});

	it('forwards rows prop', async () => {
		const screen = render(ShTextarea, { rows: 5 });
		await expect.element(screen.getByRole('textbox')).toHaveAttribute('rows', '5');
	});
});
