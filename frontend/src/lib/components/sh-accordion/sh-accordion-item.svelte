<script lang="ts">
	import AccordionItem from '$lib/components/ui/accordion/accordion-item.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof AccordionItem> = $props();
</script>

<AccordionItem class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</AccordionItem>
