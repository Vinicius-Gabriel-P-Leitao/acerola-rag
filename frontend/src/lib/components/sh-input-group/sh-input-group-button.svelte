<script lang="ts">
	import InputGroupButton from '$lib/components/ui/input-group/input-group-button.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof InputGroupButton> = $props();
</script>

<InputGroupButton class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</InputGroupButton>
