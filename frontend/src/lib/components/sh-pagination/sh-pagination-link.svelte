<script lang="ts">
	import PaginationLink from '$lib/components/ui/pagination/pagination-link.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof PaginationLink> = $props();
</script>

<PaginationLink class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</PaginationLink>
