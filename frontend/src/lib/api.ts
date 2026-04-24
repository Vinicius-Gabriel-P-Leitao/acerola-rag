const BASE_URL = import.meta.env.VITE_API_URL ?? '/api/v1';

class ApiError extends Error {
	constructor(
		public status: number,
		message: string,
		public code?: string,
		public detail?: unknown
	) {
		super(message);
		this.name = 'ApiError';
	}
}

async function getErrorData(
	res: Response
): Promise<{ message: string; code?: string; detail?: unknown }> {
	try {
		const contentType = res.headers.get('Content-Type');
		if (contentType?.includes('application/json')) {
			const data = await res.json();
			return {
				message: data.error || data.detail || data.message || 'Erro desconhecido',
				code: data.code,
				detail: data.detail
			};
		}

		const text = await res.text();
		// Bloqueia renderização de HTML grotesco (CDN/Proxy timeouts)
		if (
			text.trim().toLowerCase().startsWith('<!doctype') ||
			text.trim().toLowerCase().includes('<html')
		) {
			return {
				message: `Falha na comunicação com o servidor (${res.status}). O serviço pode estar temporariamente indisponível ou em timeout.`,
				code: `HTTP_${res.status}`
			};
		}

		return { message: text || res.statusText, code: `HTTP_${res.status}` };
	} catch {
		return { message: res.statusText || 'Erro de rede', code: `HTTP_${res.status}` };
	}
}

async function request<T>(
	method: string,
	path: string,
	body?: unknown,
	params?: Record<string, string>
): Promise<T> {
	const finalPath = `${BASE_URL}${path}`.replace('//', '/');
	const url = new URL(finalPath, window.location.origin);

	if (params) {
		for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
	}

	const init: RequestInit = {
		method,
		cache: 'no-store',
		headers: {}
	};
	if (body !== undefined) {
		(init.headers as Record<string, string>)['Content-Type'] = 'application/json';
		init.body = JSON.stringify(body);
	}

	const res = await fetch(url.toString(), init);
	if (!res.ok) {
		const errorData = await getErrorData(res);
		throw new ApiError(res.status, errorData.message, errorData.code, errorData.detail);
	}

	return res.json() as Promise<T>;
}

async function postForm<T>(path: string, form: FormData): Promise<T> {
	const finalPath = `${BASE_URL}${path}`.replace('//', '/');
	const res = await fetch(finalPath, { method: 'POST', body: form });
	if (!res.ok) {
		const errorData = await getErrorData(res);
		throw new ApiError(res.status, errorData.message, errorData.code, errorData.detail);
	}
	return res.json() as Promise<T>;
}

async function postFormStream(
	path: string,
	form: FormData,
	onToken: (token: string) => void,
	onError: (error: Error) => void
): Promise<void> {
	const finalPath = `${BASE_URL}${path}`.replace('//', '/');

	try {
		const res = await fetch(finalPath, { method: 'POST', body: form });

		if (!res.ok) {
			const errorData = await getErrorData(res);
			throw new ApiError(res.status, errorData.message, errorData.code, errorData.detail);
		}

		if (!res.body) {
			throw new Error('Resposta vazia do servidor');
		}

		const reader = res.body.getReader();
		const decoder = new TextDecoder('utf-8');

		try {
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				const chunk = decoder.decode(value, { stream: true });
				if (chunk) onToken(chunk);
			}
		} catch (err) {
			onError(err instanceof Error ? err : new Error(String(err)));
		} finally {
			reader.releaseLock();
		}
	} catch (err) {
		onError(err instanceof Error ? err : new Error(String(err)));
	}
}

export const api = {
	get: <T>(path: string, params?: Record<string, string>) =>
		request<T>('GET', path, undefined, params),
	post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
	delete: <T>(path: string) => request<T>('DELETE', path),
	postForm,
	postFormStream
};

export { ApiError };
