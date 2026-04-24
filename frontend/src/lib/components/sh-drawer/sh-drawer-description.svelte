<script lang="ts">
	import { DrawerDescription } from '$lib/components/ui/drawer';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof DrawerDescription> = $props();
</script>

<DrawerDescription class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DrawerDescription>
