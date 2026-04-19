<script lang="ts">
	import CommandEmpty from '$lib/components/ui/command/command-empty.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof CommandEmpty> = $props();
</script>

<CommandEmpty class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</CommandEmpty>
