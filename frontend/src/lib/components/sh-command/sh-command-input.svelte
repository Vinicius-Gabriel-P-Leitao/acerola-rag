<script lang="ts">
	import CommandInput from '$lib/components/ui/command/command-input.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, ...restProps }: ComponentProps<typeof CommandInput> = $props();
</script>

<CommandInput class={cn(className)} {...restProps} />
