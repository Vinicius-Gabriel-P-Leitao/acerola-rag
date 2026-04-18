<script lang="ts">
	import Sonner from '$lib/components/ui/sonner/sonner.svelte';
	import type { ComponentProps } from 'svelte';

	let { ...restProps }: ComponentProps<typeof Sonner> = $props();
</script>

<Sonner {...restProps} />
