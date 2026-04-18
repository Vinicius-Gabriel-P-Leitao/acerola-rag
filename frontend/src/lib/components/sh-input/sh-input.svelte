<script lang="ts">
	import Input from '$lib/components/ui/input/input.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		ref = $bindable(null),
		value = $bindable(),
		files = $bindable(),
		...restProps
	}: ComponentProps<typeof Input> = $props();
</script>

<Input bind:ref bind:value bind:files class={cn(className)} {...restProps} />
