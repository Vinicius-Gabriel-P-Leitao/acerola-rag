const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

class ApiError extends Error {
	constructor(
		public status: number,
		message: string
	) {
		super(message);
		this.name = 'ApiError';
	}
}

async function request<T>(
	method: string,
	path: string,
	body?: unknown,
	params?: Record<string, string>
): Promise<T> {
	const url = new URL(`${BASE_URL}${path}`);
	if (params) {
		for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
	}

	const init: RequestInit = { method };
	if (body !== undefined) {
		init.headers = { 'Content-Type': 'application/json' };
		init.body = JSON.stringify(body);
	}

	const res = await fetch(url.toString(), init);
	if (!res.ok) {
		const text = await res.text().catch(() => res.statusText);
		throw new ApiError(res.status, text);
	}
	return res.json() as Promise<T>;
}

async function postForm<T>(path: string, form: FormData): Promise<T> {
	const res = await fetch(`${BASE_URL}${path}`, { method: 'POST', body: form });
	if (!res.ok) {
		const text = await res.text().catch(() => res.statusText);
		throw new ApiError(res.status, text);
	}
	return res.json() as Promise<T>;
}

export const api = {
	get: <T>(path: string, params?: Record<string, string>) =>
		request<T>('GET', path, undefined, params),
	post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
	delete: <T>(path: string) => request<T>('DELETE', path),
	postForm
};

export { ApiError };
