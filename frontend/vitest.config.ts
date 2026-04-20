import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, defineProject } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';

export default defineConfig({
	test: {
		passWithNoTests: true,
		projects: [
			defineProject({
				plugins: [tailwindcss(), sveltekit()],
				test: {
					name: 'unit',
					environment: 'jsdom',
					include: ['src/**/*.test.ts'],
					exclude: ['src/**/*.svelte.test.ts', 'node_modules/**']
				}
			}),
			defineProject({
				plugins: [tailwindcss(), sveltekit()],
				test: {
					name: 'browser',
					include: ['src/**/*.svelte.test.ts'],
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
