import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShButton from './sh-button.svelte';

describe('ShButton', () => {
	it('renders a button element', async () => {
		const screen = render(ShButton);
		await expect.element(screen.getByRole('button')).toBeInTheDocument();
	});

	it('forwards class prop via cn', async () => {
		const screen = render(ShButton, { class: 'custom-class' });
		await expect.element(screen.getByRole('button')).toHaveClass('custom-class');
	});

	it('forwards variant prop', async () => {
		const screen = render(ShButton, { variant: 'outline' });
		await expect.element(screen.getByRole('button')).toBeInTheDocument();
	});

	it('forwards disabled prop', async () => {
		const screen = render(ShButton, { disabled: true });
		await expect.element(screen.getByRole('button')).toBeDisabled();
	});

	it('renders as anchor when href is provided', async () => {
		const screen = render(ShButton, { href: '/test' });
		await expect.element(screen.getByRole('link')).toBeInTheDocument();
	});
});
