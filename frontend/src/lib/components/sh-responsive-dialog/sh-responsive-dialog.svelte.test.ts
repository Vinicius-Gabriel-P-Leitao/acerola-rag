import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { readable } from 'svelte/store';
import { createRawSnippet } from 'svelte';

vi.mock('$lib/hooks/ui/use-mobile.hook', () => ({
	mobileStore: readable(false)
}));

function makeSnippet(text: string) {
	return createRawSnippet(() => ({
		render: () => `<span>${text}</span>`,
		setup: () => {}
	}));
}

describe('ShResponsiveDialog (desktop — dialog)', () => {
	beforeEach(() => {
		vi.resetModules();
	});

	it('renders without throwing when closed', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		expect(() => render(ShResponsiveDialog, { open: false })).not.toThrow();
	});

	it('renders without throwing when open', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		expect(() => render(ShResponsiveDialog, { open: true })).not.toThrow();
	});

	it('renders title snippet content when open', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		const screen = render(ShResponsiveDialog, {
			props: { open: true, title: makeSnippet('Meu título') }
		});
		await expect.element(screen.getByText('Meu título')).toBeInTheDocument();
	});

	it('renders description snippet content when open', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		const screen = render(ShResponsiveDialog, {
			props: { open: true, description: makeSnippet('Minha descrição') }
		});
		await expect.element(screen.getByText('Minha descrição')).toBeInTheDocument();
	});

	it('renders children snippet content when open', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		const screen = render(ShResponsiveDialog, {
			props: { open: true, children: makeSnippet('Conteúdo do corpo') }
		});
		await expect.element(screen.getByText('Conteúdo do corpo')).toBeInTheDocument();
	});

	it('renders footer snippet content when open', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		const screen = render(ShResponsiveDialog, {
			props: { open: true, footer: makeSnippet('Ação do footer') }
		});
		await expect.element(screen.getByText('Ação do footer')).toBeInTheDocument();
	});
});

describe('ShResponsiveDialog (mobile — drawer)', () => {
	beforeEach(() => {
		vi.resetModules();
		vi.doMock('$lib/hooks/ui/use-mobile.hook', () => ({
			mobileStore: readable(true)
		}));
	});

	it('renders without throwing on mobile when closed', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		expect(() => render(ShResponsiveDialog, { open: false })).not.toThrow();
	});

	it('renders without throwing on mobile when open', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		expect(() => render(ShResponsiveDialog, { open: true })).not.toThrow();
	});

	it('renders title snippet content on mobile when open', async () => {
		const { default: ShResponsiveDialog } = await import('./sh-responsive-dialog.svelte');
		const screen = render(ShResponsiveDialog, {
			props: { open: true, title: makeSnippet('Título mobile') }
		});
		await expect.element(screen.getByText('Título mobile')).toBeInTheDocument();
	});
});
