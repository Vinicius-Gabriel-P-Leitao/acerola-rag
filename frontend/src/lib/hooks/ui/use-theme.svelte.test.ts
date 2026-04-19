import { describe, it, expect, beforeEach } from 'vitest';

describe('themeStore', () => {
	beforeEach(() => {
		document.documentElement.removeAttribute('data-theme');
		localStorage.clear();
	});

	it('defaults to light theme', async () => {
		const { themeStore } = await import('./use-theme.hook');
		expect(themeStore.theme).toBe('light');
		expect(themeStore.isDark).toBe(false);
	});

	it('toggle switches to dark and sets data-theme attribute', async () => {
		const { themeStore } = await import('./use-theme.hook');
		themeStore.set('light');
		themeStore.toggle();

		expect(themeStore.theme).toBe('dark');
		expect(document.documentElement.getAttribute('data-theme')).toBe('main-theme-dark');
	});

	it('toggle back to light removes data-theme attribute', async () => {
		const { themeStore } = await import('./use-theme.hook');
		themeStore.set('dark');
		themeStore.toggle();

		expect(themeStore.theme).toBe('light');
		expect(document.documentElement.getAttribute('data-theme')).toBeNull();
	});

	it('set persists to localStorage', async () => {
		const { themeStore } = await import('./use-theme.hook');
		themeStore.set('dark');

		expect(localStorage.getItem('acerola-theme')).toBe('dark');
	});
});
