<script lang="ts">
	import InputGroupText from '$lib/components/ui/input-group/input-group-text.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof InputGroupText> = $props();
</script>

<InputGroupText class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</InputGroupText>
