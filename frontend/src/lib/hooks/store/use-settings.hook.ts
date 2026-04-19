import { writable, get } from 'svelte/store';
import { api } from '$lib/api';

export const PROVIDERS = ['openai', 'ollama', 'gemini', 'claude'] as const;
export type Provider = (typeof PROVIDERS)[number];

// TODO: Referenciar o arquivo no backend que reforça isso, se o backend só tenta usar esse modelo é pura burrice, fortificar o backend
export const PROVIDER_LABELS: Record<Provider, string> = {
	openai: 'OpenAI',
	ollama: 'Ollama (local)',
	gemini: 'Google Gemini',
	claude: 'Anthropic Claude'
};

// TODO: Referenciar o arquivo no backend que reforça isso, se o backend só tenta usar esse modelo é pura burrice, fortificar o backend
export const PROVIDER_MODELS: Record<Provider, string[]> = {
	openai: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'o3-mini'],
	ollama: ['llama3.2', 'mistral', 'codellama', 'qwen2.5'],
	gemini: ['gemini-3-flash-preview', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro'],
	claude: ['claude-sonnet-4-6', 'claude-haiku-4-5-20251001', 'claude-opus-4-7']
};

interface SettingsState {
	provider: Provider;
	model: string;
	configured: boolean;
	loading: boolean;
	error: string | null;
}

function createSettingsStore() {
	const _store = writable<SettingsState>({
		model: PROVIDER_MODELS.openai[0],
		provider: 'openai',
		configured: false,
		loading: false,
		error: null
	});

	async function load() {
		_store.update((s) => ({ ...s, loading: true }));
		try {
			const data = await api.get<{ provider: Provider; model: string; configured: boolean }>(
				'/settings'
			);

			const provider = data.provider ?? 'openai';

			_store.update((store) => ({
				...store,
				provider,
				model: data.model ?? PROVIDER_MODELS[provider][0],
				configured: data.configured,
				error: null,
				loading: false
			}));
		} catch {
			_store.update((error) => ({
				...error,
				error: 'Falha ao carregar configurações',
				loading: false
			}));
		}
	}

	async function apply(provider: Provider, model: string) {
		_store.update((store) => ({ ...store, loading: true }));

		try {
			const data = await api.post<{ configured: boolean }>('/settings', {
				llm_provider: provider,
				llm_model: model
			});
			_store.update((store) => ({
				...store,
				provider,
				model,
				configured: data.configured,
				error: data.configured
					? null
					: `API key para ${PROVIDER_LABELS[provider]} não encontrada no .env`,
				loading: false
			}));
		} catch {
			_store.update((error) => ({
				...error,
				error: 'Falha ao salvar configurações',
				loading: false
			}));
		}
	}

	function modelsForProvider(p: Provider): string[] {
		return PROVIDER_MODELS[p];
	}

	return {
		subscribe: _store.subscribe,
		get provider() {
			return get(_store).provider;
		},
		get model() {
			return get(_store).model;
		},
		get configured() {
			return get(_store).configured;
		},
		get loading() {
			return get(_store).loading;
		},
		get error() {
			return get(_store).error;
		},
		load,
		apply,
		modelsForProvider
	};
}

export const settingsStore = createSettingsStore();
