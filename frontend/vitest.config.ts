import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, defineProject } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';

export default defineConfig({
	plugins: [tailwindcss() as any, sveltekit() as any],
	test: {
		projects: [
			defineProject({
				plugins: [tailwindcss() as any, sveltekit() as any],
				test: {
					name: 'unit',
					environment: 'jsdom',
					include: ['src/**/*.test.ts'],
					exclude: ['src/**/*.svelte.test.ts', 'node_modules/**'],
					passWithNoTests: true
				}
			}),
			defineProject({
				plugins: [tailwindcss() as any, sveltekit() as any],
				test: {
					name: 'browser',
					include: ['src/**/*.svelte.test.ts'],
					passWithNoTests: true,
					browser: {
						enabled: true,
						provider: playwright(),
						instances: [{ browser: 'chromium' }]
					}
				}
			})
		]
	}
});
