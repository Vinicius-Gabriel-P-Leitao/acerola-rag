import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShCommand from './sh-command.svelte';
import ShCommandInput from './sh-command-input.svelte';

describe('ShCommand', () => {
	it('renders without throwing', () => {
		expect(() => render(ShCommand)).not.toThrow();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShCommand, { class: 'command-class' });
		expect(container.querySelector('.command-class')).not.toBeNull();
	});
});

describe('ShCommandInput', () => {
	it('renders without throwing', () => {
		expect(() => render(ShCommandInput)).not.toThrow();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShCommandInput, { class: 'input-class' });
		expect(container.querySelector('.input-class')).not.toBeNull();
	});
});
