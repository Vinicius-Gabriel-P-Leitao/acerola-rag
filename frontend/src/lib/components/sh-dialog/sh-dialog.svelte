<script lang="ts">
	import Dialog from '$lib/components/ui/dialog/dialog.svelte';
	import type { ComponentProps } from 'svelte';

	let { open = $bindable(false), children, ...restProps }: ComponentProps<typeof Dialog> = $props();
</script>

<Dialog bind:open {...restProps}>
	{#if children}{@render children()}{/if}
</Dialog>
