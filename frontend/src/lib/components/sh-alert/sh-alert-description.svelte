<script lang="ts">
	import AlertDescription from '$lib/components/ui/alert/alert-description.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof AlertDescription> = $props();
</script>

<AlertDescription class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</AlertDescription>
