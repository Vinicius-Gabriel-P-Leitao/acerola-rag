import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShSpinner from './sh-spinner.svelte';

describe('ShSpinner', () => {
	it('renders with status role', async () => {
		const screen = render(ShSpinner);
		await expect.element(screen.getByRole('status')).toBeInTheDocument();
	});

	it('has accessible label by default', async () => {
		const screen = render(ShSpinner);
		await expect.element(screen.getByRole('status')).toHaveAttribute('aria-label', 'Loading');
	});

	it('forwards custom aria-label', async () => {
		const screen = render(ShSpinner, { 'aria-label': 'Carregando dados' });
		await expect
			.element(screen.getByRole('status'))
			.toHaveAttribute('aria-label', 'Carregando dados');
	});

	it('forwards class prop via cn', async () => {
		const screen = render(ShSpinner, { class: 'size-8' });
		await expect.element(screen.getByRole('status')).toHaveClass('size-8');
	});
});
