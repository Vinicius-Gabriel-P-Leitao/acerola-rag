<script lang="ts">
	import { DrawerTitle } from '$lib/components/ui/drawer';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DrawerTitle> = $props();
</script>

<DrawerTitle class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DrawerTitle>
