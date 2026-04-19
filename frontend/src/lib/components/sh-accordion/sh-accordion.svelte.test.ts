import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShAccordion from './sh-accordion.svelte';

describe('ShAccordion', () => {
	it('renders without throwing', () => {
		expect(() => render(ShAccordion)).not.toThrow();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShAccordion, { type: 'single', class: 'accordion-class' });
		expect(container.querySelector('.accordion-class')).not.toBeNull();
	});

	it('accepts type prop', () => {
		expect(() => render(ShAccordion, { type: 'single' })).not.toThrow();
	});
});
