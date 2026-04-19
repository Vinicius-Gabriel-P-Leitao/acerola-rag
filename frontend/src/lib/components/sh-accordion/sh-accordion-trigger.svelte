<script lang="ts">
	import AccordionTrigger from '$lib/components/ui/accordion/accordion-trigger.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof AccordionTrigger> = $props();
</script>

<AccordionTrigger class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</AccordionTrigger>
