<script lang="ts">
	import DialogFooter from '$lib/components/ui/dialog/dialog-footer.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, children, ...restProps }: ComponentProps<typeof DialogFooter> = $props();
</script>

<DialogFooter class={cn(className)} {...restProps}>
	{#if children}{@render children()}{/if}
</DialogFooter>
