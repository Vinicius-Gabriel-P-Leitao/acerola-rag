<script lang="ts">
	import AlertTitle from '$lib/components/ui/alert/alert-title.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof AlertTitle> = $props();
</script>

<AlertTitle class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</AlertTitle>
