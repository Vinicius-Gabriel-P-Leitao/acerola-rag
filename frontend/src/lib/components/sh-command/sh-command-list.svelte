<script lang="ts">
	import CommandList from '$lib/components/ui/command/command-list.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof CommandList> = $props();
</script>

<CommandList class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</CommandList>
