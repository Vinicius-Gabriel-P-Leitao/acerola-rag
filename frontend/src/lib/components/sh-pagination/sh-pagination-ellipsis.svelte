<script lang="ts">
	import PaginationEllipsis from '$lib/components/ui/pagination/pagination-ellipsis.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof PaginationEllipsis> = $props();
</script>

<PaginationEllipsis class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</PaginationEllipsis>
