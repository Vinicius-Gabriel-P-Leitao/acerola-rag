<script lang="ts">
	import Textarea from '$lib/components/ui/textarea/textarea.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		ref = $bindable(null),
		value = $bindable(),
		...restProps
	}: ComponentProps<typeof Textarea> = $props();
</script>

<Textarea bind:ref bind:value class={cn(className)} {...restProps} />
