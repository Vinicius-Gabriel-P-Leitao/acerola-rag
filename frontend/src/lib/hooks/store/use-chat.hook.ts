import { writable, get } from 'svelte/store';
import { api } from '$lib/api';
import { historyStore, type RagSource } from './use-history.hook';

export interface AttachedFile {
	name: string;
	type: string;
	size_bytes: number;
	/** Only present client-side before sending */
	file?: File;
}

export interface Message {
	role: 'user' | 'assistant';
	content: string;
	attached_files?: AttachedFile[];
}

interface ChatState {
	messages: Message[];
	loading: boolean;
	error: string | null;
	conversationId: string | null;
	/** RAG sources for the current conversation */
	sources: RagSource[];
	/** Files queued to attach to next message (max 5) */
	pendingFiles: AttachedFile[];
}

const MAX_FILES = 5;

function createChatStore() {
	const _store = writable<ChatState>({
		messages: [],
		loading: false,
		error: null,
		conversationId: null,
		sources: [],
		pendingFiles: []
	});

	async function send(question: string) {
		const state = get(_store);
		const pending = state.pendingFiles;

		_store.update((s) => ({
			...s,
			messages: [
				...s.messages,
				{ role: 'user', content: question, attached_files: pending.length ? pending : undefined }
			],
			loading: true,
			error: null,
			pendingFiles: []
		}));

		_store.update((s) => ({
			...s,
			messages: [...s.messages, { role: 'assistant', content: '' }]
		}));

		const idx = get(_store).messages.length - 1;

		try {
			const form = new FormData();
			form.append('question', question);
			if (state.conversationId) form.append('conversation_id', state.conversationId);
			for (const pf of pending) {
				if (pf.file) form.append('files', pf.file);
			}

			const data = await (pending.length === 0
				? api.post<{
						answer: string;
						conversation_id: string;
						sources: RagSource[];
				  }>('/query', { question, conversation_id: state.conversationId })
				: api.postForm<{
						answer: string;
						conversation_id: string;
						sources: RagSource[];
				  }>('/query', form));

			_store.update((s) => {
				const msgs = [...s.messages];
				msgs[idx] = { role: 'assistant', content: data.answer };
				return {
					...s,
					messages: msgs,
					loading: false,
					conversationId: data.conversation_id,
					sources: data.sources ?? []
				};
			});

			// Update sidebar history
			historyStore.addOrUpdate({
				id: data.conversation_id,
				title: question.slice(0, 60),
				created_at: new Date().toISOString(),
				updated_at: new Date().toISOString()
			});
		} catch (error: unknown) {
			const msg = error instanceof Error ? error.message : 'Erro ao consultar a API';
			_store.update((s) => {
				const msgs = [...s.messages];
				msgs[idx] = { role: 'assistant', content: `❌ ${msg}` };
				return { ...s, messages: msgs, loading: false, error: msg };
			});
		}
	}

	function clear() {
		_store.set({
			messages: [],
			loading: false,
			error: null,
			conversationId: null,
			sources: [],
			pendingFiles: []
		});
	}

	async function loadConversation(conversationId: string) {
		try {
			const detail = await historyStore.getDetail(conversationId);
			_store.set({
				messages: detail.messages.map((m) => ({
					role: m.role as 'user' | 'assistant',
					content: m.content,
					attached_files: m.attached_files
				})),
				loading: false,
				error: null,
				conversationId,
				sources: detail.sources,
				pendingFiles: []
			});
		} catch {
			clear();
		}
	}

	function attachFile(file: File) {
		const state = get(_store);
		if (state.pendingFiles.length >= MAX_FILES) return;
		const already = state.pendingFiles.some((f) => f.name === file.name);
		if (already) return;
		const pf: AttachedFile = {
			name: file.name,
			type: file.name.split('.').pop() ?? 'file',
			size_bytes: file.size,
			file
		};
		_store.update((s) => ({ ...s, pendingFiles: [...s.pendingFiles, pf] }));
	}

	function removeFile(name: string) {
		_store.update((s) => ({
			...s,
			pendingFiles: s.pendingFiles.filter((f) => f.name !== name)
		}));
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
		get conversationId() {
			return get(_store).conversationId;
		},
		get sources() {
			return get(_store).sources;
		},
		get pendingFiles() {
			return get(_store).pendingFiles;
		},
		send,
		clear,
		loadConversation,
		attachFile,
		removeFile
	};
}

export const chatStore = createChatStore();
