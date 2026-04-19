<script lang="ts">
	import InputGroupInput from '$lib/components/ui/input-group/input-group-input.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		value = $bindable(),
		...restProps
	}: ComponentProps<typeof InputGroupInput> = $props();
</script>

<InputGroupInput bind:value class={cn(className)} {...restProps} />
