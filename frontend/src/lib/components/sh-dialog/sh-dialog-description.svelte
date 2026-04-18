<script lang="ts">
	import DialogDescription from '$lib/components/ui/dialog/dialog-description.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof DialogDescription> = $props();
</script>

<DialogDescription class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DialogDescription>
