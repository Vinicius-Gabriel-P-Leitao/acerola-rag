<script lang="ts">
	import Command from '$lib/components/ui/command/command.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof Command> = $props();
</script>

<Command class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</Command>
