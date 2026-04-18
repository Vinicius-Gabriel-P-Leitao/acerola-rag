<script lang="ts">
	import DialogTrigger from '$lib/components/ui/dialog/dialog-trigger.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		children,
		...restProps
	}: ComponentProps<typeof DialogTrigger> = $props();
</script>

<DialogTrigger class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DialogTrigger>
