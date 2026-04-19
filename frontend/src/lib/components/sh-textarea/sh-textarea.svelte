<script lang="ts">
	import Textarea from '$lib/components/ui/textarea/textarea.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		element = $bindable(null),
		value = $bindable(),
		...restProps
	}: ComponentProps<typeof Textarea> & { element?: HTMLTextAreaElement | null } = $props();
</script>

<Textarea bind:ref={element} bind:value class={cn(className)} {...restProps} />
