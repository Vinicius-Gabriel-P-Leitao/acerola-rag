<script lang="ts">
	import CommandGroup from '$lib/components/ui/command/command-group.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof CommandGroup> = $props();
</script>

<CommandGroup class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</CommandGroup>
