<script lang="ts">
	import CommandItem from '$lib/components/ui/command/command-item.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof CommandItem> = $props();
</script>

<CommandItem class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</CommandItem>
