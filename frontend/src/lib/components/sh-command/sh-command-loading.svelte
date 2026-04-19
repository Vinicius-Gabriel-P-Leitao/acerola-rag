<script lang="ts">
	import CommandLoading from '$lib/components/ui/command/command-loading.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof CommandLoading> = $props();
</script>

<CommandLoading class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</CommandLoading>
