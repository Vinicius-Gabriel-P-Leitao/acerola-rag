import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('$lib/api', () => ({
	api: {
		get: vi.fn(),
		delete: vi.fn()
	}
}));

import { api } from '$lib/api';

const CONV_A = {
	id: 'a1',
	title: 'Conversa A',
	created_at: '2026-01-01T00:00:00Z',
	updated_at: '2026-01-02T00:00:00Z'
};
const CONV_B = {
	id: 'b2',
	title: 'Conversa B',
	created_at: '2026-01-03T00:00:00Z',
	updated_at: '2026-01-04T00:00:00Z'
};

describe('historyStore', () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it('load() fetches and stores conversations', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ conversations: [CONV_A, CONV_B] });
		const { historyStore } = await import('./use-history.hook');

		await historyStore.load();

		expect(api.get).toHaveBeenCalledWith('/history');
		expect(historyStore.conversations.length).toBe(2);
		expect(historyStore.conversations[0].id).toBe('a1');
	});

	it('load() silently ignores API errors', async () => {
		vi.mocked(api.get).mockRejectedValueOnce(new Error('network'));
		const { historyStore } = await import('./use-history.hook');

		await expect(historyStore.load()).resolves.not.toThrow();
	});

	it('search() with query hits search endpoint', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ conversations: [CONV_A] });
		const { historyStore } = await import('./use-history.hook');

		await historyStore.search('conversa');

		expect(api.get).toHaveBeenCalledWith('/history/search', { q: 'conversa' });
		expect(historyStore.conversations[0].id).toBe('a1');
	});

	it('search() with empty string calls load() instead', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ conversations: [CONV_B] });
		const { historyStore } = await import('./use-history.hook');

		await historyStore.search('');

		expect(api.get).toHaveBeenCalledWith('/history');
	});

	it('remove() calls delete endpoint and removes from list', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ conversations: [CONV_A, CONV_B] });
		vi.mocked(api.delete).mockResolvedValueOnce({});
		const { historyStore } = await import('./use-history.hook');

		await historyStore.load();
		await historyStore.remove('a1');

		expect(api.delete).toHaveBeenCalledWith('/history/a1');
		expect(historyStore.conversations.find((c) => c.id === 'a1')).toBeUndefined();
		expect(historyStore.conversations.length).toBe(1);
	});

	it('addOrUpdate() adds new conversation at front', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ conversations: [CONV_A] });
		const { historyStore } = await import('./use-history.hook');
		await historyStore.load();

		historyStore.addOrUpdate(CONV_B);

		expect(historyStore.conversations[0].id).toBe('b2');
		expect(historyStore.conversations.length).toBe(2);
	});

	it('addOrUpdate() updates existing conversation in place', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({ conversations: [CONV_A] });
		const { historyStore } = await import('./use-history.hook');
		await historyStore.load();

		const updated = { ...CONV_A, title: 'Título atualizado' };
		historyStore.addOrUpdate(updated);

		expect(historyStore.conversations.length).toBe(1);
		expect(historyStore.conversations[0].title).toBe('Título atualizado');
	});

	it('getDetail() fetches conversation detail', async () => {
		const detail = {
			id: 'a1',
			title: 'Conversa A',
			messages: [
				{ id: 1, role: 'user', content: 'oi', created_at: '2026-01-01', attached_files: [] }
			],
			sources: []
		};
		vi.mocked(api.get).mockResolvedValueOnce(detail);
		const { historyStore } = await import('./use-history.hook');

		const result = await historyStore.getDetail('a1');

		expect(api.get).toHaveBeenCalledWith('/history/a1');
		expect(result.id).toBe('a1');
		expect(result.messages.length).toBe(1);
	});
});
