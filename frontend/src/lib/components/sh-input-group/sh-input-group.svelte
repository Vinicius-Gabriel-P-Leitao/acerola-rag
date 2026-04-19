<script lang="ts">
	import InputGroup from '$lib/components/ui/input-group/input-group.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof InputGroup> = $props();
</script>

<InputGroup class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</InputGroup>
