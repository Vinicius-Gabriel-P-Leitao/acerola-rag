import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShPagination from './sh-pagination.svelte';
import ShPaginationContent from './sh-pagination-content.svelte';
import ShPaginationItem from './sh-pagination-item.svelte';
import ShPaginationEllipsis from './sh-pagination-ellipsis.svelte';

describe('ShPagination', () => {
	it('renders a nav element', async () => {
		const screen = render(ShPagination, { count: 0 });
		await expect.element(screen.getByRole('navigation')).toBeInTheDocument();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShPagination, { count: 0, class: 'pagination-class' });
		expect(container.querySelector('.pagination-class')).not.toBeNull();
	});
});

describe('ShPaginationContent', () => {
	it('renders without throwing', () => {
		expect(() => render(ShPaginationContent)).not.toThrow();
	});
});

describe('ShPaginationItem', () => {
	it('renders without throwing', () => {
		expect(() => render(ShPaginationItem)).not.toThrow();
	});
});

describe('ShPaginationEllipsis', () => {
	it('renders without throwing', () => {
		expect(() => render(ShPaginationEllipsis)).not.toThrow();
	});
});
