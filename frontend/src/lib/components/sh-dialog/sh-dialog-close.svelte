<script lang="ts">
	import DialogClose from '$lib/components/ui/dialog/dialog-close.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DialogClose> = $props();
</script>

<DialogClose class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DialogClose>
