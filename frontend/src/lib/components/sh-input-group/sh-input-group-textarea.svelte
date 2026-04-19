<script lang="ts">
	import InputGroupTextarea from '$lib/components/ui/input-group/input-group-textarea.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		value = $bindable(),
		...restProps
	}: ComponentProps<typeof InputGroupTextarea> = $props();
</script>

<InputGroupTextarea bind:value class={cn(className)} {...restProps} />
