<script lang="ts">
	import { DrawerFooter } from '$lib/components/ui/drawer';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DrawerFooter> = $props();
</script>

<DrawerFooter class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DrawerFooter>
