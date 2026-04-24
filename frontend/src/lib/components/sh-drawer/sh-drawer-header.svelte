<script lang="ts">
	import { DrawerHeader } from '$lib/components/ui/drawer';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DrawerHeader> = $props();
</script>

<DrawerHeader class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DrawerHeader>
