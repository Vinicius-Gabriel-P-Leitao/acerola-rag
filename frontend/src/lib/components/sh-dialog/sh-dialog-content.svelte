<script lang="ts">
	import DialogContent from '$lib/components/ui/dialog/dialog-content.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DialogContent> = $props();
</script>

<DialogContent class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DialogContent>
