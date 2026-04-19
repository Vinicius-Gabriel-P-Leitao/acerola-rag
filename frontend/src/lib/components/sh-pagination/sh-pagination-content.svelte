<script lang="ts">
	import PaginationContent from '$lib/components/ui/pagination/pagination-content.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof PaginationContent> = $props();
</script>

<PaginationContent class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</PaginationContent>
