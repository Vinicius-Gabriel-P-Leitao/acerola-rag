<script lang="ts">
	import CommandSeparator from '$lib/components/ui/command/command-separator.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, ...restProps }: ComponentProps<typeof CommandSeparator> = $props();
</script>

<CommandSeparator class={cn(className)} {...restProps} />
