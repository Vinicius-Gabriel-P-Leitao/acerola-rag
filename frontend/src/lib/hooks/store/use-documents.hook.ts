import { writable, get, derived } from 'svelte/store';
import { api } from '$lib/api';

export interface DocumentMeta {
	source: string;
	file_type: string;
	file_size_bytes: number;
	uploaded_at: string;
	word_count: number;
}

export interface DocumentsPage {
	total: number;
	items: DocumentMeta[];
}

export interface QueueJob {
	job_id: string;
	filename: string;
	status: 'pending' | 'processing' | 'done' | 'error';
	error: string | null;
	created_at: string;
	finished_at: string | null;
}

interface DocumentsState {
	page: number;
	pageSize: number;
	search: string;
	total: number;
	items: DocumentMeta[];
	loading: boolean;
	error: string | null;
	jobs: QueueJob[];
}

function createDocumentsStore() {
	const _store = writable<DocumentsState>({
		page: 1,
		pageSize: 10,
		search: '',
		total: 0,
		items: [],
		loading: false,
		error: null,
		jobs: []
	});

	const _totalPages = derived(_store, (s) => Math.max(1, Math.ceil(s.total / s.pageSize)));

	async function fetchPage() {
		_store.update((s) => ({ ...s, loading: true, error: null }));
		try {
			const { page, pageSize, search } = get(_store);
			const data = await api.get<DocumentsPage>('/documents', {
				page: String(page),
				page_size: String(pageSize),
				search
			});
			_store.update((s) => ({ ...s, total: data.total, items: data.items, loading: false }));
		} catch {
			_store.update((s) => ({ ...s, error: 'Falha ao carregar documentos', loading: false }));
		}
	}

	async function fetchQueue() {
		try {
			const data = await api.get<{ jobs: QueueJob[] }>('/upload/status');
			_store.update((s) => ({ ...s, jobs: data.jobs }));
		} catch {
			// silently ignore queue errors
		}
	}

	async function deleteDocument(source: string): Promise<number> {
		const data = await api.delete<{ deleted_chunks: number }>(`/documents/${source}`);
		await fetchPage();
		return data.deleted_chunks;
	}

	async function getContent(source: string): Promise<string> {
		const data = await api.get<{ content: string }>(`/documents/${source}/content`);
		return data.content;
	}

	async function uploadFiles(files: File[]): Promise<void> {
		const form = new FormData();
		for (const f of files) form.append('files', f);
		await api.postForm('/upload', form);
	}

	async function indexText(title: string, content: string): Promise<{ job_id: string }> {
		return api.post('/documents/text', { title, content });
	}

	function setPage(p: number) {
		_store.update((s) => ({ ...s, page: p }));
		fetchPage();
	}

	function setSearch(s: string) {
		_store.update((st) => ({ ...st, search: s, page: 1 }));
		fetchPage();
	}

	return {
		subscribe: _store.subscribe,
		get page() {
			return get(_store).page;
		},
		get pageSize() {
			return get(_store).pageSize;
		},
		get search() {
			return get(_store).search;
		},
		get total() {
			return get(_store).total;
		},
		get items() {
			return get(_store).items;
		},
		get loading() {
			return get(_store).loading;
		},
		get error() {
			return get(_store).error;
		},
		get jobs() {
			return get(_store).jobs;
		},
		get totalPages() {
			return get(_totalPages);
		},
		fetchPage,
		fetchQueue,
		deleteDocument,
		getContent,
		uploadFiles,
		indexText,
		setPage,
		setSearch
	};
}

export const documentsStore = createDocumentsStore();
