<script lang="ts">
	import PaginationNext from '$lib/components/ui/pagination/pagination-next.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof PaginationNext> = $props();
</script>

<PaginationNext class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</PaginationNext>
