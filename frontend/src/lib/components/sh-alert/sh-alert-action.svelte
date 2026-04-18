<script lang="ts">
	import AlertAction from '$lib/components/ui/alert/alert-action.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof AlertAction> = $props();
</script>

<AlertAction class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</AlertAction>
