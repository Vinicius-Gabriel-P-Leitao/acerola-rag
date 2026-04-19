import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('$lib/api', () => ({
	api: {
		post: vi.fn()
	}
}));

import { api } from '$lib/api';

describe('chatStore', () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it('appends user and assistant messages on send', async () => {
		vi.mocked(api.post).mockResolvedValueOnce({ answer: 'Resposta da IA' });

		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		await chatStore.send('Olá');

		expect(chatStore.messages.length).toBe(2);
		expect(chatStore.messages[0]).toEqual({ role: 'user', content: 'Olá' });
		expect(chatStore.messages[1]).toEqual({ role: 'assistant', content: 'Resposta da IA' });
	});

	it('sets error message on API failure', async () => {
		vi.mocked(api.post).mockRejectedValueOnce(new Error('timeout'));

		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		await chatStore.send('pergunta');

		const last = chatStore.messages.at(-1);
		expect(last?.content).toContain('❌');
		expect(chatStore.error).toBeTruthy();
	});

	it('clear() removes all messages', async () => {
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		expect(chatStore.messages.length).toBe(0);
	});
});
