<script lang="ts">
	import CommandDialog from '$lib/components/ui/command/command-dialog.svelte';
	import type { ComponentProps } from 'svelte';

	let {
		open = $bindable(false),
		children,
		...restProps
	}: ComponentProps<typeof CommandDialog> = $props();
</script>

<CommandDialog bind:open {...restProps}>
	{#if children}{@render children()}{/if}
</CommandDialog>
