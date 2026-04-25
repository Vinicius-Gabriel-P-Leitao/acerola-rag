import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { page } from '@vitest/browser/context';
import SourcesModal from './sources-modal.svelte';

vi.mock('$lib/api', () => ({
	api: {
		get: vi.fn()
	}
}));

import { api } from '$lib/api';

const SOURCES = [
	{ source_file: 'relatorio.pdf', chunk_text: 'Trecho do relatório aqui.', score: 0.92 },
	{ source_file: 'manual.docx', chunk_text: 'Trecho do manual técnico.', score: 0.75 }
];

describe('SourcesModal', () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it('renders nothing visible when closed', async () => {
		render(SourcesModal, { open: false, sources: SOURCES });
		const dialog = page.getByRole('dialog');
		await expect.element(dialog).not.toBeInTheDocument();
	});

	it('shows source list when open', async () => {
		render(SourcesModal, { open: true, sources: SOURCES });
		await expect.element(page.getByText('Fontes da conversa (2)')).toBeVisible();
		await expect.element(page.getByText('relatorio.pdf')).toBeVisible();
		await expect.element(page.getByText('manual.docx')).toBeVisible();
	});

	it('shows score as percentage', async () => {
		render(SourcesModal, { open: true, sources: SOURCES });
		await expect.element(page.getByText('92%')).toBeVisible();
		await expect.element(page.getByText('75%')).toBeVisible();
	});

	it('filters sources by filename when searching', async () => {
		render(SourcesModal, { open: true, sources: SOURCES });
		const input = page.getByPlaceholder('Buscar por arquivo…');
		await input.fill('relatorio');

		await expect.element(page.getByText('relatorio.pdf')).toBeVisible();
		await expect.element(page.getByText('manual.docx')).not.toBeInTheDocument();
	});

	it('shows empty message when search has no match', async () => {
		render(SourcesModal, { open: true, sources: SOURCES });
		await page.getByPlaceholder('Buscar por arquivo…').fill('inexistente');

		await expect.element(
			page.getByText('Nenhuma fonte encontrada para essa busca.')
		).toBeVisible();
	});

	it('navigates to document view on eye button click', async () => {
		vi.mocked(api.get).mockResolvedValue({ content: 'Conteúdo completo do doc.' });
		render(SourcesModal, { open: true, sources: SOURCES });

		await page.getByTitle('Ver documento completo').first().click();

		// Document view shows back button and the readonly textarea with content
		await expect.element(page.getByRole('button', { name: 'Voltar' })).toBeVisible();
		const textarea = page.getByRole('textbox');
		await expect.element(textarea).toBeVisible();
	});

	it('leaves the list view while document is loading', async () => {
		let resolve!: (v: { content: string }) => void;
		vi.mocked(api.get).mockReturnValue(new Promise((r) => (resolve = r)));

		render(SourcesModal, { open: true, sources: SOURCES });
		await page.getByTitle('Ver documento completo').first().click();

		// Once navigation happens, the list title disappears
		await expect.element(page.getByText('Fontes da conversa (2)')).not.toBeInTheDocument();

		// Resolve to avoid Svelte reactivity-loss warnings on teardown
		resolve({ content: 'done' });
		await new Promise((r) => setTimeout(r, 0));
	});

	it('shows back button in document view', async () => {
		vi.mocked(api.get).mockResolvedValue({ content: 'texto' });
		render(SourcesModal, { open: true, sources: SOURCES });
		await page.getByTitle('Ver documento completo').first().click();

		await expect.element(page.getByRole('button', { name: 'Voltar' })).toBeVisible();
	});

	it('back button returns to source list', async () => {
		vi.mocked(api.get).mockResolvedValue({ content: 'texto' });
		render(SourcesModal, { open: true, sources: SOURCES });
		await page.getByTitle('Ver documento completo').first().click();
		await page.getByRole('button', { name: 'Voltar' }).click();

		await expect.element(page.getByText('Fontes da conversa (2)')).toBeVisible();
	});

	it('shows error message when document fetch fails', async () => {
		vi.mocked(api.get).mockRejectedValue(new Error('not found'));
		render(SourcesModal, { open: true, sources: SOURCES });
		await page.getByTitle('Ver documento completo').first().click();

		await expect
			.element(page.getByText('Não foi possível carregar o conteúdo do documento.'))
			.toBeVisible();
	});
});
