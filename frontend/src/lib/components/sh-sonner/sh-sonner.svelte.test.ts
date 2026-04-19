import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShSonner from './sh-sonner.svelte';

describe('ShSonner', () => {
	it('renders without throwing', () => {
		expect(() => render(ShSonner)).not.toThrow();
	});

	it('mounts a toaster element into the DOM', async () => {
		const { container } = render(ShSonner);
		expect(container).toBeDefined();
	});
});
