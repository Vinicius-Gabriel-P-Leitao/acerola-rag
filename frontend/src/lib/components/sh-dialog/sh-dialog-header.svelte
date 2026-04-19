<script lang="ts">
	import DialogHeader from '$lib/components/ui/dialog/dialog-header.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DialogHeader> = $props();
</script>

<DialogHeader class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DialogHeader>
