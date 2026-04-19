import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('$lib/api', () => ({
	api: {
		get: vi.fn(),
		post: vi.fn()
	}
}));

import { api } from '$lib/api';
import { PROVIDER_MODELS, PROVIDERS, PROVIDER_LABELS } from './use-settings.hook';

describe('settings store constants', () => {
	it('has all four providers', () => {
		expect(PROVIDERS).toContain('openai');
		expect(PROVIDERS).toContain('ollama');
		expect(PROVIDERS).toContain('gemini');
		expect(PROVIDERS).toContain('claude');
	});

	it('has label for every provider', () => {
		for (const p of PROVIDERS) {
			expect(PROVIDER_LABELS[p]).toBeTruthy();
		}
	});

	it('has at least one model per provider', () => {
		for (const p of PROVIDERS) {
			expect(PROVIDER_MODELS[p].length).toBeGreaterThan(0);
		}
	});

	it('includes claude-sonnet-4-6 in claude models', () => {
		expect(PROVIDER_MODELS.claude).toContain('claude-sonnet-4-6');
	});

	it('includes gemini-3-flash-preview in gemini models', () => {
		expect(PROVIDER_MODELS.gemini).toContain('gemini-3-flash-preview');
	});
});

describe('settingsStore', () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it('loads settings from API', async () => {
		vi.mocked(api.get).mockResolvedValueOnce({
			provider: 'claude',
			model: 'claude-sonnet-4-6',
			configured: true
		});

		const { settingsStore } = await import('./use-settings.hook');
		await settingsStore.load();

		expect(settingsStore.provider).toBe('claude');
		expect(settingsStore.model).toBe('claude-sonnet-4-6');
		expect(settingsStore.configured).toBe(true);
	});

	it('sets error when API key is missing', async () => {
		vi.mocked(api.post).mockResolvedValueOnce({ configured: false });

		const { settingsStore } = await import('./use-settings.hook');
		await settingsStore.apply('openai', 'gpt-4o');

		expect(settingsStore.error).toBeTruthy();
	});

	it('clears error on successful apply', async () => {
		vi.mocked(api.post).mockResolvedValueOnce({ configured: true });

		const { settingsStore } = await import('./use-settings.hook');
		await settingsStore.apply('openai', 'gpt-4o-mini');

		expect(settingsStore.error).toBeNull();
	});
});
