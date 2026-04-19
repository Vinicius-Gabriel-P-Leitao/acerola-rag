<script lang="ts">
	import Pagination from '$lib/components/ui/pagination/pagination.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, ...restProps }: ComponentProps<typeof Pagination> = $props();
</script>

<Pagination class={cn(className)} {...restProps} />
