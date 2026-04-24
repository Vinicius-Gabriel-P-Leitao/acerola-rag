import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { createRawSnippet } from 'svelte';
import ShExpandable from './sh-expandable.svelte';

function makeSnippet(html: string) {
	return createRawSnippet(() => ({
		render: () => html,
		setup: () => {}
	}));
}

describe('ShExpandable', () => {
	it('renders children content', async () => {
		const screen = render(ShExpandable, {
			props: { children: makeSnippet('<p>conteúdo visível</p>') }
		});
		await expect.element(screen.getByText('conteúdo visível')).toBeInTheDocument();
	});

	it('does not show toggle button when content is short', async () => {
		const screen = render(ShExpandable, {
			props: { children: makeSnippet('<p>curto</p>'), threshold: 9999 }
		});
		const button = screen.getByRole('button');
		// button should not be in document when no truncation needed
		await expect.element(button).not.toBeInTheDocument();
	});

	it('shows "Ver mais" button when threshold is very small', async () => {
		const longHtml = '<p>' + 'texto longo '.repeat(40) + '</p>';
		const screen = render(ShExpandable, {
			props: { children: makeSnippet(longHtml), threshold: 1 }
		});
		await expect.element(screen.getByRole('button', { name: /ver mais/i })).toBeInTheDocument();
	});

	it('toggles to "Ver menos" when clicked', async () => {
		const longHtml = '<p>' + 'expandir '.repeat(40) + '</p>';
		const screen = render(ShExpandable, {
			props: { children: makeSnippet(longHtml), threshold: 1 }
		});
		const button = screen.getByRole('button', { name: /ver mais/i });
		await button.click();
		await expect.element(screen.getByRole('button', { name: /ver menos/i })).toBeInTheDocument();
	});

	it('forwards class prop', async () => {
		const screen = render(ShExpandable, {
			props: { children: makeSnippet('<p>x</p>'), class: 'minha-classe' }
		});
		const wrapper = screen.container.firstElementChild;
		expect(wrapper?.classList.contains('minha-classe')).toBe(true);
	});
});
