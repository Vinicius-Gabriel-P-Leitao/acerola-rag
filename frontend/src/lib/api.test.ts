import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api, ApiError } from './api';

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

function makeResponse(body: unknown, ok = true, status = 200) {
	return {
		ok,
		status,
		statusText: ok ? 'OK' : 'Error',
		json: () => Promise.resolve(body),
		text: () => Promise.resolve(String(body))
	};
}

describe('api client', () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it('GET resolves with parsed JSON', async () => {
		mockFetch.mockResolvedValueOnce(makeResponse({ provider: 'openai' }));
		const result = await api.get('/settings');
		expect(result).toEqual({ provider: 'openai' });
	});

	it('GET passes query params', async () => {
		mockFetch.mockResolvedValueOnce(makeResponse({ total: 0, items: [] }));
		await api.get('/documents', { page: '1', search: 'test' });
		const url = mockFetch.mock.calls[0][0] as string;
		expect(url).toContain('page=1');
		expect(url).toContain('search=test');
	});

	it('POST sends JSON body with correct headers', async () => {
		mockFetch.mockResolvedValueOnce(makeResponse({ configured: true }));
		await api.post('/settings', { llm_provider: 'openai' });
		const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
		expect(init.method).toBe('POST');
		expect((init.headers as Record<string, string>)['Content-Type']).toBe('application/json');
		expect(init.body).toContain('llm_provider');
	});

	it('DELETE sends correct method', async () => {
		mockFetch.mockResolvedValueOnce(makeResponse({ deleted_chunks: 3 }));
		await api.delete('/documents/doc.pdf');
		const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
		expect(init.method).toBe('DELETE');
	});

	it('throws ApiError on non-ok response', async () => {
		mockFetch.mockResolvedValueOnce(makeResponse('Not found', false, 404));
		await expect(api.get('/missing')).rejects.toBeInstanceOf(ApiError);
	});

	it('ApiError carries status code', async () => {
		mockFetch.mockResolvedValueOnce(makeResponse('Unprocessable', false, 422));
		try {
			await api.get('/bad');
		} catch (err) {
			expect((err as ApiError).status).toBe(422);
		}
	});
});
