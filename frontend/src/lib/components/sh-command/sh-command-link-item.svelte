<script lang="ts">
	import CommandLinkItem from '$lib/components/ui/command/command-link-item.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof CommandLinkItem> = $props();
</script>

<CommandLinkItem class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</CommandLinkItem>
