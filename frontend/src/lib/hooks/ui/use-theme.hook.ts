import { writable, get } from 'svelte/store';

type Theme = 'light' | 'dark';

const STORAGE_KEY = 'acerola-theme';
const DARK_ATTR = 'main-theme-dark';

function createThemeStore() {
	const _store = writable<Theme>('light');

	function applyTheme(t: Theme) {
		const root = document.documentElement;
		if (t === 'dark') {
			root.setAttribute('data-theme', DARK_ATTR);
		} else {
			root.removeAttribute('data-theme');
		}
	}

	function init() {
		if (typeof window === 'undefined') return;
		const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
		const theme =
			stored ?? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
		_store.set(theme);
		applyTheme(theme);
	}

	function toggle() {
		const next = get(_store) === 'light' ? 'dark' : 'light';
		_store.set(next);
		localStorage.setItem(STORAGE_KEY, next);
		applyTheme(next);
	}

	function set(t: Theme) {
		_store.set(t);
		localStorage.setItem(STORAGE_KEY, t);
		applyTheme(t);
	}

	return {
		subscribe: _store.subscribe,
		get theme() {
			return get(_store);
		},
		get isDark() {
			return get(_store) === 'dark';
		},
		init,
		toggle,
		set
	};
}

export const themeStore = createThemeStore();
