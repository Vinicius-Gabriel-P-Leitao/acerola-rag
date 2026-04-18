<script lang="ts">
	import PaginationPrevious from '$lib/components/ui/pagination/pagination-previous.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof PaginationPrevious> = $props();
</script>

<PaginationPrevious class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</PaginationPrevious>
