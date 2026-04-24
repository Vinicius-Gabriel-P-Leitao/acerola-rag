import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('$lib/api', () => ({
	api: {
		postForm: vi.fn(),
		get: vi.fn()
	}
}));

vi.mock('./use-history.hook', () => ({
	historyStore: {
		addOrUpdate: vi.fn(),
		load: vi.fn(),
		search: vi.fn(),
		getDetail: vi.fn(),
		remove: vi.fn(),
		subscribe: vi.fn(() => () => {}),
		get conversations() {
			return [];
		},
		get loading() {
			return false;
		}
	}
}));

import { api } from '$lib/api';

const SUCCESS_RESPONSE = {
	answer: '<ContentResponse>\nResposta da IA\n</ContentResponse>',
	conversation_id: 'conv-test-123',
	sources: [{ source_file: 'doc.pdf', chunk_text: 'trecho', score: 0.9 }]
};

describe('chatStore', () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it('appends user and assistant messages on send', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		await chatStore.send('Olá');

		expect(chatStore.messages.length).toBe(2);
		expect(chatStore.messages[0].role).toBe('user');
		expect(chatStore.messages[0].content).toBe('Olá');
		expect(chatStore.messages[1].role).toBe('assistant');
		expect(chatStore.messages[1].content).toBe(SUCCESS_RESPONSE.answer);
	});

	it('stores conversation_id from response', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		await chatStore.send('pergunta');

		expect(chatStore.conversationId).toBe('conv-test-123');
	});

	it('stores sources from response', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		await chatStore.send('pergunta');

		expect(chatStore.sources.length).toBe(1);
		expect(chatStore.sources[0].source_file).toBe('doc.pdf');
	});

	it('sends existing conversation_id in subsequent messages', async () => {
		vi.mocked(api.postForm).mockResolvedValue(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		await chatStore.send('primeira');
		await chatStore.send('segunda');

		const secondCall = vi.mocked(api.postForm).mock.calls[1];
		const form = secondCall[1] as FormData;
		expect(form.get('conversation_id')).toBe('conv-test-123');
	});

	it('sends FormData not JSON', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		await chatStore.send('teste');

		expect(api.postForm).toHaveBeenCalledWith('/query', expect.any(FormData));
	});

	it('includes question in FormData', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		await chatStore.send('minha pergunta');

		const form = vi.mocked(api.postForm).mock.calls[0][1] as FormData;
		expect(form.get('question')).toBe('minha pergunta');
	});

	it('sets error message on API failure', async () => {
		vi.mocked(api.postForm).mockRejectedValueOnce(new Error('timeout'));
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		await chatStore.send('pergunta');

		const last = chatStore.messages.at(-1);
		expect(last?.content).toContain('❌');
		expect(chatStore.error).toBeTruthy();
	});

	it('clear() resets all state', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		await chatStore.send('algo');
		chatStore.clear();

		expect(chatStore.messages.length).toBe(0);
		expect(chatStore.conversationId).toBeNull();
		expect(chatStore.sources.length).toBe(0);
		expect(chatStore.pendingFiles.length).toBe(0);
	});

	it('attachFile adds file to pendingFiles', async () => {
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		const file = new File(['content'], 'doc.pdf', { type: 'application/pdf' });

		chatStore.attachFile(file);

		expect(chatStore.pendingFiles.length).toBe(1);
		expect(chatStore.pendingFiles[0].name).toBe('doc.pdf');
	});

	it('attachFile respects max 5 file limit', async () => {
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		for (let i = 0; i < 7; i++) {
			chatStore.attachFile(new File(['x'], `file${i}.pdf`));
		}

		expect(chatStore.pendingFiles.length).toBe(5);
	});

	it('attachFile ignores duplicate file names', async () => {
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();

		chatStore.attachFile(new File(['a'], 'same.pdf'));
		chatStore.attachFile(new File(['b'], 'same.pdf'));

		expect(chatStore.pendingFiles.length).toBe(1);
	});

	it('removeFile removes by name', async () => {
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		chatStore.attachFile(new File(['a'], 'keep.pdf'));
		chatStore.attachFile(new File(['b'], 'remove.pdf'));

		chatStore.removeFile('remove.pdf');

		expect(chatStore.pendingFiles.length).toBe(1);
		expect(chatStore.pendingFiles[0].name).toBe('keep.pdf');
	});

	it('send clears pendingFiles after sending', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		chatStore.attachFile(new File(['x'], 'anexo.pdf'));

		await chatStore.send('com arquivo');

		expect(chatStore.pendingFiles.length).toBe(0);
	});

	it('send includes pending files in FormData', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		const file = new File(['content'], 'anexo.txt', { type: 'text/plain' });
		chatStore.attachFile(file);

		await chatStore.send('com arquivo');

		const form = vi.mocked(api.postForm).mock.calls[0][1] as FormData;
		expect(form.getAll('files').length).toBe(1);
	});

	it('pending files appear in user message attached_files', async () => {
		vi.mocked(api.postForm).mockResolvedValueOnce(SUCCESS_RESPONSE);
		const { chatStore } = await import('./use-chat.hook');
		chatStore.clear();
		chatStore.attachFile(new File(['x'], 'doc.pdf'));

		await chatStore.send('com arquivo');

		const userMsg = chatStore.messages[0];
		expect(userMsg.attached_files?.length).toBe(1);
		expect(userMsg.attached_files?.[0].name).toBe('doc.pdf');
	});
});
