<script lang="ts">
	import { Drawer } from '$lib/components/ui/drawer';
	import type { ComponentProps } from 'svelte';

	let {
		open = $bindable(false),
		children,
		...restProps
	}: ComponentProps<typeof Drawer> = $props();
</script>

<Drawer bind:open {...restProps}>
	{#if children}{@render children()}{/if}
</Drawer>
