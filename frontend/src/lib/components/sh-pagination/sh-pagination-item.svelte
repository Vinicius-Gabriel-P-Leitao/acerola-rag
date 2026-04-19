<script lang="ts">
	import PaginationItem from '$lib/components/ui/pagination/pagination-item.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof PaginationItem> = $props();
</script>

<PaginationItem class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</PaginationItem>
