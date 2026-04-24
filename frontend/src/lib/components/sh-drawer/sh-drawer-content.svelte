<script lang="ts">
	import { DrawerContent } from '$lib/components/ui/drawer';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DrawerContent> = $props();
</script>

<DrawerContent class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DrawerContent>
