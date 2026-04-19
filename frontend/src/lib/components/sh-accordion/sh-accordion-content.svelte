<script lang="ts">
	import AccordionContent from '$lib/components/ui/accordion/accordion-content.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof AccordionContent> = $props();
</script>

<AccordionContent class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</AccordionContent>
