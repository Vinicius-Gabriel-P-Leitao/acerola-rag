import { writable, get } from 'svelte/store';

const MOBILE_BREAKPOINT = 768;

function createMobileStore() {
	const _store = writable(false);

	function init() {
		if (typeof window === 'undefined') return;
		const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`);
		_store.set(mql.matches);
		mql.addEventListener('change', (e) => _store.set(e.matches));
	}

	return {
		subscribe: _store.subscribe,
		get isMobile() {
			return get(_store);
		},
		init
	};
}

export const mobileStore = createMobileStore();
