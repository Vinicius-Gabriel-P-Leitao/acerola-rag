import { writable, get } from 'svelte/store';
import { api } from '$lib/api';

export interface Conversation {
	id: string;
	title: string;
	created_at: string;
	updated_at: string;
}

export interface RagSource {
	source_file: string;
	chunk_text: string;
	score: number;
}

export interface ConversationDetail {
	id: string;
	title: string;
	messages: {
		id: number;
		role: string;
		content: string;
		created_at: string;
		attached_files: { name: string; type: string; size_bytes: number }[];
	}[];
	sources: RagSource[];
}

interface HistoryState {
	conversations: Conversation[];
	loading: boolean;
	searchQuery: string;
}

	function createHistoryStore() {
	// Usar um valor padrão seguro em ambiente de teste
	const isBrowser = typeof window !== 'undefined' && typeof localStorage !== 'undefined';
	const saved = isBrowser && typeof localStorage.getItem === 'function' 
		? localStorage.getItem('acerola_history') 
		: null;
	const initial = saved ? JSON.parse(saved) : [];

	const _store = writable<HistoryState>({
		conversations: initial,
		loading: false,
		searchQuery: ''
	});

	// Assina para salvar sempre que mudar
	_store.subscribe((s) => {
		if (isBrowser && typeof localStorage.setItem === 'function') {
			localStorage.setItem('acerola_history', JSON.stringify(s.conversations));
		}
	});


	async function load() {
		_store.update((s) => ({ ...s, loading: true }));
		try {
			const data = await api.get<{ conversations: Conversation[] }>('/history');
			_store.set({ 
				conversations: data.conversations || [], 
				loading: false,
				searchQuery: '' 
			});
		} catch (error) {
			console.error('Failed to load history:', error);
			_store.update((s) => ({ ...s, loading: false }));
		}
	}

	async function search(q: string) {
		_store.update((s) => ({ ...s, searchQuery: q }));
		if (!q.trim()) {
			load();
			return;
		}
		try {
			const data = await api.get<{ conversations: Conversation[] }>('/history/search', { q });
			_store.update((s) => ({ ...s, conversations: data.conversations }));
		} catch {
			/* keep current list on error */
		}
	}

	async function getDetail(conversationId: string): Promise<ConversationDetail> {
		return api.get<ConversationDetail>(`/history/${conversationId}`);
	}

	async function remove(conversationId: string) {
		await api.delete(`/history/${conversationId}`);
		_store.update((s) => ({
			...s,
			conversations: s.conversations.filter((c) => c.id !== conversationId)
		}));
	}

	function addOrUpdate(conv: Conversation) {
		_store.update((s) => {
			const exists = s.conversations.find((c) => c.id === conv.id);
			if (exists) {
				return {
					...s,
					conversations: s.conversations.map((c) => (c.id === conv.id ? conv : c))
				};
			}
			return { ...s, conversations: [conv, ...s.conversations] };
		});
	}

	return {
		subscribe: _store.subscribe,
		get conversations() {
			return get(_store).conversations;
		},
		get loading() {
			return get(_store).loading;
		},
		load,
		search,
		getDetail,
		remove,
		addOrUpdate
	};
}

export const historyStore = createHistoryStore();
