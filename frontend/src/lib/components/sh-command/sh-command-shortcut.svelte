<script lang="ts">
	import CommandShortcut from '$lib/components/ui/command/command-shortcut.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof CommandShortcut> = $props();
</script>

<CommandShortcut class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</CommandShortcut>
