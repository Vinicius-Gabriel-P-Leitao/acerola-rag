import { getContext, setContext, type Snippet } from 'svelte';

export class HeaderState {
	title = $state('');
	action = $state<Snippet | null>(null);
}

const HEADER_KEY = Symbol('header');

export function initHeader() {
	return setContext(HEADER_KEY, new HeaderState());
}

export function useHeader() {
	return getContext<HeaderState>(HEADER_KEY);
}
