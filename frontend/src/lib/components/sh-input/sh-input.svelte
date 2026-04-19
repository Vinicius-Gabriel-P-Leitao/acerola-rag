<script lang="ts">
	import Input from '$lib/components/ui/input/input.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	type Props = ComponentProps<typeof Input>;

	let {
		class: className,
		ref = $bindable(null),
		value = $bindable(),
		files = $bindable(),
		type,
		...restProps
	}: Props = $props();
</script>

{#if type === 'file'}
	<Input bind:ref bind:value bind:files class={cn(className)} type="file" {...restProps} />
{:else}
	<Input bind:ref bind:value class={cn(className)} {type} {...restProps} />
{/if}
