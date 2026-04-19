<script lang="ts">
	import Spinner from '$lib/components/ui/spinner/spinner.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, ...restProps }: ComponentProps<typeof Spinner> = $props();
</script>

<Spinner class={cn(className)} {...restProps} />
