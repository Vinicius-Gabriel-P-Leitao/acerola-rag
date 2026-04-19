<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import type { ButtonProps } from '$lib/components/ui/button/button.svelte';
	import { cn } from '$lib/utils';

	let { class: className, ref = $bindable(null), children, ...restProps }: ButtonProps = $props();
</script>

<Button bind:ref class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</Button>
