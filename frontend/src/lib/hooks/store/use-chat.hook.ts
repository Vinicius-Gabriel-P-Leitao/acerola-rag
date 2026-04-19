import { writable, get } from 'svelte/store';
import { api } from '$lib/api';

export interface Message {
	role: 'user' | 'assistant';
	content: string;
}

interface ChatState {
	messages: Message[];
	loading: boolean;
	error: string | null;
}

function createChatStore() {
	const _store = writable<ChatState>({ messages: [], loading: false, error: null });

	async function send(question: string) {
		_store.update((s) => ({
			...s,
			messages: [...s.messages, { role: 'user', content: question }],
			loading: true,
			error: null
		}));
		_store.update((s) => ({
			...s,
			messages: [...s.messages, { role: 'assistant', content: '' }]
		}));
		const idx = get(_store).messages.length - 1;

		try {
			const data = await api.post<{ answer: string }>('/query', { question });
			_store.update((s) => {
				const msgs = [...s.messages];
				msgs[idx] = { role: 'assistant', content: data.answer };
				return { ...s, messages: msgs, loading: false };
			});
		} catch (err: unknown) {
			const msg = err instanceof Error ? err.message : 'Erro ao consultar a API';
			_store.update((s) => {
				const msgs = [...s.messages];
				msgs[idx] = { role: 'assistant', content: `❌ ${msg}` };
				return { ...s, messages: msgs, loading: false, error: msg };
			});
		}
	}

	function clear() {
		_store.set({ messages: [], loading: false, error: null });
	}

	return {
		subscribe: _store.subscribe,
		get messages() {
			return get(_store).messages;
		},
		get loading() {
			return get(_store).loading;
		},
		get error() {
			return get(_store).error;
		},
		send,
		clear
	};
}

export const chatStore = createChatStore();
