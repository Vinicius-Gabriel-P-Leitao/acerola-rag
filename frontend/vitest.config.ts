import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [tailwindcss() as any, sveltekit() as any],
	test: {
		environment: 'jsdom',
		include: ['src/**/*.test.ts'],
		exclude: ['src/**/*.svelte.test.ts', 'node_modules/**'],
		passWithNoTests: true
	}
});
