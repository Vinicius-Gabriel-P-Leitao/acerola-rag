import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import ShCommand from './sh-command.svelte';
import ShCommandInputWrapper from './sh-command-input-wrapper.test.svelte';

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
		expect(() => render(ShCommandInputWrapper)).not.toThrow();
	});

	it('forwards class prop via cn', async () => {
		const { container } = render(ShCommandInputWrapper, { class: 'input-class' });
		expect(container.querySelector('.input-class')).not.toBeNull();
	});
});
