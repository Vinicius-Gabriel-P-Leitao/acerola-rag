import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShSkeleton from './sh-skeleton.svelte';

describe('ShSkeleton', () => {
	it('renders with data-slot attribute', async () => {
		const { container } = render(ShSkeleton);
		const el = container.querySelector('[data-slot="skeleton"]');
		expect(el).not.toBeNull();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShSkeleton, { class: 'w-32 h-4' });
		const el = container.querySelector('[data-slot="skeleton"]');
		expect(el?.classList.contains('w-32')).toBe(true);
		expect(el?.classList.contains('h-4')).toBe(true);
	});

	it('includes animate-pulse from shadcn base', async () => {
		const { container } = render(ShSkeleton);
		const el = container.querySelector('[data-slot="skeleton"]');
		expect(el?.classList.contains('animate-pulse')).toBe(true);
	});
});
