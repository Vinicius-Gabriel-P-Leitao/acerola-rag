<script lang="ts">
	import Alert from '$lib/components/ui/alert/alert.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof Alert> = $props();
</script>

<Alert class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</Alert>
