<script lang="ts">
	import Accordion from '$lib/components/ui/accordion/accordion.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof Accordion> = $props();
</script>

<Accordion class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</Accordion>
