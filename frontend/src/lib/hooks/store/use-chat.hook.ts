import { writable, get } from 'svelte/store';
import { api } from '$lib/api';
import { historyStore, type RagSource } from './use-history.hook';

export interface AttachedFileDTO {
	name: string;
	type: string;
	size_bytes: number;
}

export interface MessageDTO {
	id: number;
	role: string;
	content: string;
	created_at: string;
	attached_files: AttachedFileDTO[];
}

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
	isError?: boolean;
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
		const convId = state.conversationId ?? crypto.randomUUID();

		_store.update((s) => ({
			...s,
			messages: [
				...s.messages,
				{ role: 'user', content: question, attached_files: pending.length ? pending : undefined }
			],
			loading: true,
			error: null,
			pendingFiles: [],
			conversationId: convId
		}));

		_store.update((s) => ({
			...s,
			messages: [...s.messages, { role: 'assistant', content: '' }]
		}));

		const idx = get(_store).messages.length - 1;

		try {
			const form = new FormData();
			form.append('question', question);
			form.append('conversation_id', convId);
			for (const pf of pending) {
				if (pf.file) form.append('files', pf.file);
			}

			await api.postFormStream(
				'/query/stream',
				form,
				(token) => {
					_store.update((s) => {
						const msgs = [...s.messages];
						msgs[idx] = {
							...msgs[idx],
							content: msgs[idx].content + token
						};
						return { ...s, messages: msgs };
					});
				},
				(error) => {
					_store.update((s) => {
						const msgs = [...s.messages];
						msgs[idx] = {
							...msgs[idx],
							content: error.message,
							isError: true
						};
						return { ...s, messages: msgs, loading: false };
					});
				}
			);

			// Busca sources do histórico após o stream terminar
			try {
				const detail = await historyStore.getDetail(convId);
				_store.update((s) => ({ ...s, sources: detail.sources, loading: false }));
			} catch {
				_store.update((s) => ({ ...s, loading: false }));
			}
		} catch (error: unknown) {
			const msg = error instanceof Error ? error.message : 'Erro ao consultar a API';
			_store.update((s) => {
				const msgs = [...s.messages];
				msgs[idx] = { role: 'assistant', content: msg, isError: true, attached_files: [] };
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
					attached_files: m.attached_files.map((f) => ({
						name: f.name,
						type: f.type,
						size_bytes: f.size_bytes
					}))
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
