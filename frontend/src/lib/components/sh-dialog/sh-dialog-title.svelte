<script lang="ts">
	import DialogTitle from '$lib/components/ui/dialog/dialog-title.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DialogTitle> = $props();
</script>

<DialogTitle class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DialogTitle>
