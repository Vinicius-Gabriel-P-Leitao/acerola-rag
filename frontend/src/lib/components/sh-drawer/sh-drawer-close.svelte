<script lang="ts">
	import { DrawerClose } from '$lib/components/ui/drawer';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DrawerClose> = $props();
</script>

<DrawerClose class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DrawerClose>
