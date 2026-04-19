import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
	{
		plugins: [tailwindcss() as any, sveltekit() as any],
		test: {
			name: 'unit',
			environment: 'jsdom',
			include: ['src/**/*.test.ts'],
			exclude: ['src/**/*.svelte.test.ts', 'node_modules/**'],
			passWithNoTests: true
		}
	}
]);
