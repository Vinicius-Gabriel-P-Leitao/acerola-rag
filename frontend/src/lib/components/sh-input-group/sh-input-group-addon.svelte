<script lang="ts">
	import InputGroupAddon from '$lib/components/ui/input-group/input-group-addon.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof InputGroupAddon> = $props();
</script>

<InputGroupAddon class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</InputGroupAddon>
