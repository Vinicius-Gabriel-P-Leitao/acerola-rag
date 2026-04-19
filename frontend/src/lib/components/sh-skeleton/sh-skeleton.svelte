<script lang="ts">
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let {
		class: className,
		ref = $bindable(null),
		...restProps
	}: ComponentProps<typeof Skeleton> = $props();
</script>

<Skeleton bind:ref class={cn(className)} {...restProps} />
