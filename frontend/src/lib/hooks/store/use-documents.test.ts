import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('$lib/api', () => ({
	api: {
		get: vi.fn(),
		post: vi.fn(),
		delete: vi.fn(),
		postForm: vi.fn()
	}
}));

vi.mock('svelte-sonner', () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

import { api } from '$lib/api';

describe('documentsStore', () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it('fetches page and sets items', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({
			total: 2,
			items: [
				{
					source: 'doc1.pdf',
					file_type: 'pdf',
					file_size_bytes: 1024,
					uploaded_at: '2025-01-01T00:00:00',
					word_count: 500
				},
				{
					source: 'doc2.txt',
					file_type: 'text',
					file_size_bytes: 512,
					uploaded_at: '2025-01-02T00:00:00',
					word_count: 100
				}
			]
		});

		const { documentsStore } = await import('./use-documents.hook');
		await documentsStore.fetchPage();

		expect(documentsStore.total).toBe(2);
		expect(documentsStore.items.length).toBe(2);
		expect(documentsStore.items[0].source).toBe('doc1.pdf');
	});

	it('computes totalPages correctly', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ total: 25, items: [] });

		const { documentsStore } = await import('./use-documents.hook');
		await documentsStore.fetchPage();

		expect(documentsStore.totalPages).toBe(3);
	});

	it('deleteDocument calls API and refreshes', async () => {
		vi.mocked(api.delete).mockResolvedValueOnce({ deleted_chunks: 5 });
		vi.mocked(api.get).mockResolvedValueOnce({ total: 0, items: [] });

		const { documentsStore } = await import('./use-documents.hook');
		const count = await documentsStore.deleteDocument('doc1.pdf');

		expect(count).toBe(5);
		expect(api.delete).toHaveBeenCalledWith('/documents/doc1.pdf');
	});

	it('getContent returns document text', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ content: 'conteúdo do doc' });

		const { documentsStore } = await import('./use-documents.hook');
		const content = await documentsStore.getContent('doc1.pdf');

		expect(content).toBe('conteúdo do doc');
	});

	it('indexText posts to /documents/text', async () => {
		vi.mocked(api.post).mockResolvedValueOnce({ job_id: 'abc123', filename: 'meu-doc.txt' });

		const { documentsStore } = await import('./use-documents.hook');
		const result = await documentsStore.indexText('meu-doc', 'conteúdo aqui');

		expect(api.post).toHaveBeenCalledWith('/documents/text', {
			title: 'meu-doc',
			content: 'conteúdo aqui'
		});
		expect(result).toMatchObject({ job_id: 'abc123' });
	});

	it('setPage updates page and fetches', async () => {
		vi.mocked(api.get).mockResolvedValue({ total: 30, items: [] });

		const { documentsStore } = await import('./use-documents.hook');
		documentsStore.setPage(3);
		await new Promise((r) => setTimeout(r, 0));

		expect(documentsStore.page).toBe(3);
		expect(api.get).toHaveBeenCalledWith(
			'/documents',
			expect.objectContaining({ page: '3' })
		);
	});

	it('setSearch resets to page 1 and fetches', async () => {
		vi.mocked(api.get).mockResolvedValue({ total: 5, items: [] });

		const { documentsStore } = await import('./use-documents.hook');
		documentsStore.setPage(4);
		documentsStore.setSearch('relatorio');
		await new Promise((r) => setTimeout(r, 0));

		expect(documentsStore.page).toBe(1);
		expect(api.get).toHaveBeenCalledWith(
			'/documents',
			expect.objectContaining({ search: 'relatorio', page: '1' })
		);
	});

	it('totalPages is 1 when total is 0', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ total: 0, items: [] });

		const { documentsStore } = await import('./use-documents.hook');
		await documentsStore.fetchPage();

		expect(documentsStore.totalPages).toBe(1);
	});

	it('totalPages rounds up correctly', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ total: 11, items: [] });

		const { documentsStore } = await import('./use-documents.hook');
		await documentsStore.fetchPage();

		expect(documentsStore.totalPages).toBe(2);
	});
});
