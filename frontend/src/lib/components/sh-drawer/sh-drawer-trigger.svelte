<script lang="ts">
	import { DrawerTrigger } from '$lib/components/ui/drawer';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DrawerTrigger> = $props();
</script>

<DrawerTrigger class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DrawerTrigger>
